import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import validate


ROOT = Path(__file__).parents[1]


class ContractHardeningTests(unittest.TestCase):
    def test_draft_requires_verify_command(self):
        request = validate.load("examples/draft/draft-request.json")
        request["input"]["build"].pop("verify_command", None)

        with self.assertRaises(ValueError):
            validate.validate_request(request)

    def test_full_check_requires_complete_environment_and_build(self):
        request = validate.load("examples/e2-contract/full-check-request.json")
        request["input"].pop("environment")

        with self.assertRaises(ValueError):
            validate.validate_request(request)

    def test_incremental_check_requires_environment(self):
        request = validate.load("examples/e2-contract/incremental-check-request-c0-c1.json")
        request["input"].pop("environment")

        with self.assertRaises(ValueError):
            validate.validate_request(request)

    def test_repair_requires_target_file_and_environment(self):
        request = validate.load("examples/repair/repair-request.json")
        request["input"].pop("target_file", None)
        request["input"].pop("environment", None)

        with self.assertRaises(ValueError):
            validate.validate_request(request)

    def test_repair_report_must_match_repository_and_configuration(self):
        request = validate.load("examples/repair/repair-request.json")
        request["input"]["repository"]["commit"] = "00000000000000000000000000000000000000c1"

        with self.assertRaises(ValueError):
            validate.validate_request(request)

    def test_repair_rejects_unmapped_mock_report_uri(self):
        request = validate.load("examples/repair/repair-request.json")
        request["input"]["md_report_uri"] = (
            "artifact://pair-A01-B01/job-other-001/md-report.json"
        )

        with self.assertRaises(ValueError):
            validate.validate_request(request)

    def test_succeeded_job_requires_output_object(self):
        job = validate.load("examples/e2-contract/full-check-success.json")
        job["output"] = None

        with self.assertRaises(ValueError):
            validate.validate_job(job)

    def test_successful_repair_rejection_is_not_an_execution_error(self):
        job = validate.load("examples/b01/repair-rejected.json")

        validate.validate_job(job)
        self.assertEqual("SUCCEEDED", job["status"])
        self.assertEqual("REJECTED", job["output"]["decision"])
        self.assertIsNone(job["error"])

    def test_report_samples_are_valid(self):
        validate.validate_report(validate.load("examples/build-checker/md-rd-report-c0.json"))
        validate.validate_report(validate.load("examples/e-checker/consistency-report-c1.json"))

    def test_report_rejects_repository_relative_artifact_paths(self):
        report = copy.deepcopy(validate.load("examples/e-checker/consistency-report-c1.json"))
        report["incremental_result"] = "examples/e-checker/incremental-graph-c0-c1.json"

        with self.assertRaises(ValueError):
            validate.validate_report(report)

    def test_report_requires_location_and_evidence_for_findings(self):
        report = copy.deepcopy(validate.load("examples/build-checker/md-rd-report-c0.json"))
        report["findings"][0].pop("location")

        with self.assertRaises(ValueError):
            validate.validate_report(report)

    def test_artifacts_carry_commit_and_configuration_metadata(self):
        job = validate.load("examples/e2-contract/full-check-success.json")
        for artifact in job["output"]["artifacts"]:
            self.assertIn("commit", artifact)
            self.assertIn("configuration_id", artifact)

    def test_created_and_rejected_response_examples_exist(self):
        created = validate.load("examples/e2-contract/full-check-created.json")
        rejected = validate.load("examples/e2-contract/rejected-invalid-request.json")

        self.assertEqual(202, created["http_status"])
        self.assertEqual("QUEUED", created["job"]["status"])
        self.assertEqual(400, rejected["http_status"])
        self.assertEqual("REQUEST_REJECTED", rejected["error"]["code"])

    def test_schema_documents_record_hardening_rules(self):
        task_schema = json.loads(
            (ROOT / "schemas/task.schema.json").read_text(encoding="utf-8")
        )
        request_schema = json.loads(
            (ROOT / "schemas/job-request.schema.json").read_text(encoding="utf-8")
        )
        artifact_schema = json.loads(
            (ROOT / "schemas/artifact.schema.json").read_text(encoding="utf-8")
        )

        task_text = json.dumps(task_schema)
        request_text = json.dumps(request_schema)
        artifact_text = json.dumps(artifact_schema)
        self.assertIn("SUCCEEDED", task_text)
        self.assertIn("output", task_text)
        self.assertIn("configuration_id", request_text)
        self.assertIn("PATCH_NOTES", artifact_text)
        self.assertTrue((ROOT / "schemas/report.schema.json").exists())


if __name__ == "__main__":
    unittest.main()
