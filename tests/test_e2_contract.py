import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate


class E2ContractTests(unittest.TestCase):
    def test_all_four_task_types_have_request_and_response_samples(self):
        samples = {
            "DRAFT": (
                "examples/draft/draft-request.json",
                "examples/draft/draft-success.json",
            ),
            "FULL_CHECK": (
                "examples/e2-contract/full-check-request.json",
                "examples/e2-contract/full-check-success.json",
            ),
            "INCREMENTAL_CHECK": (
                "examples/e2-contract/incremental-check-request-c0-c1.json",
                "examples/e2-contract/incremental-check-success-c0-c1.json",
            ),
            "REPAIR": (
                "examples/repair/repair-request.json",
                "examples/repair/repair-result.json",
            ),
        }
        for job_type, (request_path, response_path) in samples.items():
            with self.subTest(job_type=job_type):
                request = validate.load(request_path)
                response = validate.load(response_path)
                validate.validate_request(request)
                validate.validate_job(response)
                self.assertEqual(job_type, request["job_type"])
                self.assertEqual(job_type, response["job_type"])

    def test_incremental_success_exposes_current_and_resolved_findings(self):
        job = validate.load("examples/e2-contract/incremental-check-success-c0-c1.json")
        output = job["output"]
        self.assertTrue(output["findings"])
        self.assertTrue(output["added_findings"])
        self.assertIsInstance(output["resolved_findings"][0], str)

    def test_successful_findings_are_distinct_from_execution_error(self):
        job = validate.load("examples/e2-contract/full-check-success.json")
        self.assertEqual("SUCCEEDED", job["status"])
        self.assertIsNone(job["error"])
        self.assertTrue(job["output"]["findings"])

    def test_end_to_end_scenario_starts_with_draft_request(self):
        scenario = validate.load("examples/end-to-end/scenario.json")
        first_stage = scenario["stages"][0]
        self.assertEqual("DRAFT", first_stage["name"])
        self.assertEqual("examples/draft/draft-request.json", first_stage["input"])


if __name__ == "__main__":
    unittest.main()
