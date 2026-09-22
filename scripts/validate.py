"""Validate the contract and mock workflow without third-party packages."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PASS_COUNT = 0


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


def validate_request(value: dict[str, Any]) -> None:
    if value.get("schema_version") != "1.0":
        raise ValueError("schema_version must be 1.0")
    if value.get("job_type") not in {"DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"}:
        raise ValueError("unsupported job_type")
    if not value.get("idempotency_key"):
        raise ValueError("idempotency_key is required")
    if not isinstance(value.get("input"), dict):
        raise ValueError("input must be an object")
    input_value = value["input"]
    if value["job_type"] == "DRAFT":
        if not isinstance(input_value.get("repository"), dict) or not input_value["repository"].get("commit"):
            raise ValueError("DRAFT requires repository.commit")
        if not isinstance(input_value.get("build"), dict) or not input_value["build"].get("command"):
            raise ValueError("DRAFT requires build.command")
    elif value["job_type"] == "FULL_CHECK":
        if not isinstance(input_value.get("repository"), dict) or not input_value["repository"].get("commit"):
            raise ValueError("FULL_CHECK requires repository.commit")
        if not isinstance(input_value.get("environment"), dict) or not input_value["environment"].get("configuration_id"):
            raise ValueError("FULL_CHECK requires environment.configuration_id")
        if not isinstance(input_value.get("build"), dict) or not input_value["build"].get("build_command"):
            raise ValueError("FULL_CHECK requires build.build_command")
    elif value["job_type"] == "REPAIR":
        if not isinstance(input_value.get("repository"), dict) or not input_value["repository"].get("commit"):
            raise ValueError("REPAIR requires repository.commit")
        if not input_value.get("md_report_uri", "").startswith("artifact://"):
            raise ValueError("REPAIR requires an MD report artifact URI")
    elif value["job_type"] == "INCREMENTAL_CHECK":
        baseline = input_value.get("baseline")
        if not isinstance(baseline, dict):
            raise ValueError("baseline is required")
        if baseline.get("commit") != input_value.get("base_commit"):
            raise ValueError("baseline commit does not match base_commit")
        current_config = input_value.get("environment", {}).get("configuration_id")
        if current_config and baseline.get("configuration_id") != current_config:
            raise ValueError("baseline configuration does not match current configuration")


def validate_job(value: dict[str, Any]) -> None:
    required = {"schema_version", "job_id", "trace_id", "job_type", "status", "input", "output", "error"}
    missing = required - value.keys()
    if missing:
        raise ValueError(f"missing canonical job fields: {sorted(missing)}")
    if value["schema_version"] != "1.0":
        raise ValueError("canonical job schema version must be 1.0")
    if value["status"] not in {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"}:
        raise ValueError("unsupported status")
    if value["status"] in {"FAILED", "TIMED_OUT"} and not isinstance(value.get("error"), dict):
        raise ValueError("failed jobs require error")
    if value["status"] == "SUCCEEDED" and value.get("error") is not None:
        raise ValueError("successful jobs must not contain an execution error")
    if value.get("error") is not None:
        if value["error"].get("code") not in {"ENV_3002", "EXEC_4002", "ANALYSIS_5001"}:
            raise ValueError("unsupported execution error code")
    output = value.get("output")
    if isinstance(output, dict):
        for artifact in output.get("artifacts", []):
            if not str(artifact.get("uri", "")).startswith("artifact://"):
                raise ValueError("artifact URI must use artifact://")
        for field in ("findings", "added_findings", "resolved_findings"):
            for finding in output.get(field, []):
                if not isinstance(finding, dict):
                    raise ValueError(f"{field} must contain finding objects")
                if finding.get("type") not in {"MISSING", "REDUNDANT"}:
                    raise ValueError("unsupported finding type")


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
    ):
        validate_job(load(relative))
    passed("canonical job responses")

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

    validate_scenario()
    print(f"{PASS_COUNT} checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        raise SystemExit(1)
