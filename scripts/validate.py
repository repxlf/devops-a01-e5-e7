"""Validate the contract and mock workflow without third-party packages."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PASS_COUNT = 0

ALLOWED_JOB_TYPES = {"DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"}
ALLOWED_STATUSES = {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"}
ALLOWED_FINDING_TYPES = {"MISSING", "REDUNDANT"}
ALLOWED_ERROR_CODES = {"ENV_3002", "EXEC_4002", "ANALYSIS_5001"}
ALLOWED_ARTIFACT_TYPES = {
    "ACTUAL_GRAPH",
    "DECLARED_GRAPH",
    "ERROR_REPORT",
    "MD_REPORT",
    "RD_REPORT",
    "PATCH",
    "PATCH_NOTES",
    "BUILD_LOG",
    "TEST_REPORT",
    "DOCKERFILE",
    "IMAGE_REF",
    "DRAFT_LOG",
}


def load(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def passed(label: str) -> None:
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"[PASS] {label}")


def expect_rejected(label: str, check) -> None:
    try:
        check()
    except ValueError:
        passed(label)
    else:
        raise AssertionError(f"expected rejection: {label}")


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def require_string(value: dict[str, Any], field: str, context: str = "input") -> str:
    result = value.get(field)
    if not isinstance(result, str) or not result:
        raise ValueError(f"{context}.{field} is required")
    return result


def validate_request(value: dict[str, Any]) -> None:
    if value.get("schema_version") != "1.0":
        raise ValueError("schema_version must be 1.0")
    job_type = value.get("job_type")
    if job_type not in ALLOWED_JOB_TYPES:
        raise ValueError("unsupported job_type")
    if not value.get("idempotency_key"):
        raise ValueError("idempotency_key is required")
    input_value = require_mapping(value.get("input"), "input")

    repository = require_mapping(input_value.get("repository"), "repository")
    require_string(repository, "commit", "input.repository")

    if job_type == "DRAFT":
        build = require_mapping(input_value.get("build"), "build")
        require_string(build, "build_command", "input.build")
        require_string(build, "verify_command", "input.build")
        limits = require_mapping(input_value.get("limits"), "limits")
        if not isinstance(limits.get("max_iterations"), int) or limits["max_iterations"] < 1:
            raise ValueError("input.limits.max_iterations must be a positive integer")
    elif job_type == "FULL_CHECK":
        environment = require_mapping(input_value.get("environment"), "environment")
        require_string(environment, "image", "input.environment")
        require_string(environment, "configuration_id", "input.environment")
        build = require_mapping(input_value.get("build"), "build")
        for field in ("project_root", "clean_command", "build_command"):
            require_string(build, field, "input.build")
    elif job_type == "INCREMENTAL_CHECK":
        require_string(input_value, "base_commit")
        environment = require_mapping(input_value.get("environment"), "environment")
        require_string(environment, "image", "input.environment")
        current_config = require_string(environment, "configuration_id", "input.environment")
        build = require_mapping(input_value.get("build"), "build")
        for field in ("project_root", "clean_command", "build_command"):
            require_string(build, field, "input.build")
        baseline = require_mapping(input_value.get("baseline"), "baseline")
        require_string(baseline, "actual_graph_uri", "input.baseline")
        baseline_commit = require_string(baseline, "commit", "input.baseline")
        baseline_config = require_string(baseline, "configuration_id", "input.baseline")
        if baseline_commit != input_value["base_commit"]:
            raise ValueError("baseline commit does not match base_commit")
        if baseline_config != current_config:
            raise ValueError("baseline configuration does not match current configuration")
    elif job_type == "REPAIR":
        report_uri = require_string(input_value, "md_report_uri")
        if not report_uri.startswith("artifact://"):
            raise ValueError("REPAIR requires an MD report artifact URI")
        require_string(input_value, "target_file")
        environment = require_mapping(input_value.get("environment"), "environment")
        require_string(environment, "image", "input.environment")
        configuration_id = require_string(environment, "configuration_id", "input.environment")
        require_string(input_value, "build_command")
        require_string(input_value, "verify_command")
        report = validate_report(load_artifact_fixture(report_uri))
        if report["commit"] != repository["commit"]:
            raise ValueError("MD report commit does not match repository commit")
        if report["configuration_id"] != configuration_id:
            raise ValueError("MD report configuration does not match environment")
        if any(finding["type"] != "MISSING" for finding in report["findings"]):
            raise ValueError("REPAIR accepts an MD report containing only MISSING findings")


def validate_artifact(artifact: dict[str, Any]) -> None:
    for field in ("artifact_id", "type", "uri", "media_type", "producer_job_id"):
        require_string(artifact, field, "artifact")
    if artifact["type"] not in ALLOWED_ARTIFACT_TYPES:
        raise ValueError(f"unsupported artifact type: {artifact['type']}")
    if not artifact["uri"].startswith("artifact://"):
        raise ValueError("artifact URI must use artifact://")
    require_string(artifact, "commit", "artifact")
    require_string(artifact, "configuration_id", "artifact")


def validate_job(value: dict[str, Any]) -> None:
    required = {"schema_version", "job_id", "trace_id", "job_type", "status", "input", "output", "error"}
    missing = required - value.keys()
    if missing:
        raise ValueError(f"missing canonical job fields: {sorted(missing)}")
    if value["schema_version"] != "1.0":
        raise ValueError("canonical job schema version must be 1.0")
    if value["job_type"] not in ALLOWED_JOB_TYPES:
        raise ValueError("unsupported job type")
    if value["status"] not in ALLOWED_STATUSES:
        raise ValueError("unsupported status")
    if value["status"] in {"FAILED", "TIMED_OUT"} and not isinstance(value.get("error"), dict):
        raise ValueError("failed jobs require error")
    if value["status"] == "SUCCEEDED":
        if not isinstance(value.get("output"), dict):
            raise ValueError("successful jobs require an output object")
        if value.get("error") is not None:
            raise ValueError("successful jobs must not contain an execution error")
    if value.get("error") is not None:
        error = require_mapping(value["error"], "error")
        if error.get("code") not in ALLOWED_ERROR_CODES:
            raise ValueError("unsupported execution error code")
        require_string(error, "message", "error")

    output = value.get("output")
    if isinstance(output, dict):
        for artifact in output.get("artifacts", []):
            validate_artifact(require_mapping(artifact, "artifact"))
        for field in ("findings", "added_findings"):
            for finding in output.get(field, []):
                finding_value = require_mapping(finding, field)
                if finding_value.get("type") not in ALLOWED_FINDING_TYPES:
                    raise ValueError("unsupported finding type")
        for finding_id in output.get("resolved_findings", []):
            if not isinstance(finding_id, str) or not finding_id:
                raise ValueError("resolved_findings must contain finding IDs")
        if value["job_type"] == "REPAIR" and output.get("decision") not in {"ACCEPTED", "REJECTED"}:
            raise ValueError("REPAIR output requires ACCEPTED or REJECTED decision")


ARTIFACT_FIXTURE_MAP = {
    "md-report.json": "examples/build-checker/md-rd-report-c0.json",
    "rd-report.json": "examples/build-checker/rd-report-c0.json",
}


def load_artifact_fixture(uri: str) -> dict[str, Any]:
    if not uri.startswith("artifact://"):
        raise ValueError("artifact URI must use artifact://")
    filename = uri.rsplit("/", 1)[-1]
    relative = ARTIFACT_FIXTURE_MAP.get(filename)
    if relative is None:
        raise ValueError(f"no mock fixture mapped for artifact URI: {uri}")
    return load(relative)


def validate_report(report: dict[str, Any]) -> dict[str, Any]:
    report_type = report.get("report_type")
    if report_type in {"MD_REPORT", "RD_REPORT"}:
        for field in ("report_id", "commit", "configuration_id"):
            require_string(report, field, "report")
        findings = report.get("findings")
        if not isinstance(findings, list):
            raise ValueError("report.findings must be an array")
        for finding in findings:
            finding_value = require_mapping(finding, "report.finding")
            if finding_value.get("type") not in ALLOWED_FINDING_TYPES:
                raise ValueError("unsupported report finding type")
            if report_type == "MD_REPORT" and finding_value["type"] != "MISSING":
                raise ValueError("MD_REPORT may contain only MISSING findings")
            if report_type == "RD_REPORT" and finding_value["type"] != "REDUNDANT":
                raise ValueError("RD_REPORT may contain only REDUNDANT findings")
        return report
    if report_type == "CONSISTENCY_REPORT":
        for field in ("comparison_id", "base_commit", "current_commit"):
            require_string(report, field, "consistency report")
        for field in ("incremental_result", "full_result"):
            uri = require_string(report, field, "consistency report")
            if not uri.startswith("artifact://"):
                raise ValueError("consistency report results must use artifact:// URIs")
        for field in ("graph_equal", "findings_equal"):
            if not isinstance(report.get(field), bool):
                raise ValueError(f"consistency report {field} must be boolean")
        for field in ("incremental_duration_ms", "full_duration_ms"):
            if not isinstance(report.get(field), int) or report[field] < 0:
                raise ValueError(f"consistency report {field} must be non-negative")
        return report
    raise ValueError("unsupported report_type")


def validate_http_response(value: dict[str, Any]) -> None:
    status = value.get("http_status")
    if status == 202:
        job = require_mapping(value.get("job"), "job")
        require_string(job, "job_id", "job")
        if job.get("status") != "QUEUED":
            raise ValueError("created job response must be QUEUED")
    elif status == 400:
        error = require_mapping(value.get("error"), "error")
        if error.get("code") != "REQUEST_REJECTED":
            raise ValueError("rejected request response must use REQUEST_REJECTED")
        require_string(error, "message", "error")
    else:
        raise ValueError("unsupported mock HTTP response status")


def validate_scenario() -> None:
    scenario = load("examples/end-to-end/scenario.json")
    for stage in scenario["stages"]:
        for key in ("input", "job", "artifacts", "result"):
            value = stage.get(key)
            if isinstance(value, str):
                if not (ROOT / value).exists():
                    raise ValueError(f"scenario reference does not exist: {value}")
            elif isinstance(value, list):
                for item in value:
                    if not (ROOT / item).exists():
                        raise ValueError(f"scenario reference does not exist: {item}")
    passed("end-to-end scenario references")


def main() -> int:
    for job_type, relative in (
        ("DRAFT", "examples/draft/draft-request.json"),
        ("FULL_CHECK", "examples/e2-contract/full-check-request.json"),
        ("INCREMENTAL_CHECK", "examples/e2-contract/incremental-check-request-c0-c1.json"),
        ("REPAIR", "examples/repair/repair-request.json"),
    ):
        request = load(relative)
        validate_request(request)
        if request["job_type"] != job_type:
            raise ValueError(f"unexpected job type in {relative}")
        passed(f"{job_type} valid request")

    for relative in (
        "examples/draft/draft-queued.json",
        "examples/draft/draft-success.json",
        "examples/e2-contract/full-check-queued.json",
        "examples/e2-contract/full-check-success.json",
        "examples/e2-contract/incremental-check-success-c0-c1.json",
        "examples/e2-contract/system-error-analysis-failed.json",
        "examples/repair/repair-result.json",
        "examples/b01/repair-rejected.json",
    ):
        validate_job(load(relative))
    passed("canonical job responses")

    for relative in (
        "examples/build-checker/md-rd-report-c0.json",
        "examples/build-checker/rd-report-c0.json",
        "examples/e-checker/consistency-report-c1.json",
    ):
        validate_report(load(relative))
    passed("report artifacts")

    for relative in (
        "examples/e2-contract/full-check-created.json",
        "examples/e2-contract/rejected-invalid-request.json",
    ):
        validate_http_response(load(relative))
    passed("HTTP creation and rejection responses")

    expect_rejected(
        "invalid job_type rejected",
        lambda: validate_request(load("examples/invalid/invalid-job-type.json")),
    )
    expect_rejected(
        "incremental request without baseline rejected",
        lambda: validate_request(load("examples/invalid/invalid-incremental-no-baseline.json")),
    )
    expect_rejected(
        "incremental request with mismatched baseline rejected",
        lambda: validate_request(load("examples/invalid/invalid-incremental-mismatched-baseline.json")),
    )
    expect_rejected(
        "draft request without verify command rejected",
        lambda: validate_request(load("examples/invalid/invalid-draft-missing-verify-command.json")),
    )
    expect_rejected(
        "repair request without target file rejected",
        lambda: validate_request(load("examples/invalid/invalid-repair-missing-target-file.json")),
    )
    expect_rejected(
        "repair request with mismatched report rejected",
        lambda: validate_request(load("examples/invalid/invalid-repair-mismatched-report.json")),
    )

    validate_scenario()
    print(f"{PASS_COUNT} checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        raise SystemExit(1)
