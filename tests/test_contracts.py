import unittest

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from a_group.contracts.models import Job
from a_group.e_checker.baseline import validate_baseline


class ContractModelTests(unittest.TestCase):
    def test_job_knows_findings_are_not_execution_errors(self):
        job = Job(
            schema_version="1.0",
            job_id="job-1",
            trace_id="trace-1",
            job_type="FULL_CHECK",
            status="SUCCEEDED",
            input={},
            output={"findings": [{"finding_id": "f-1"}]},
        )
        self.assertTrue(job.has_analysis_findings)
        self.assertIsNone(job.error)

    def test_incremental_baseline_matches_base_commit(self):
        validate_baseline(
            {
                "base_commit": "C0",
                "environment": {"configuration_id": "cc-MODE0"},
                "baseline": {"commit": "C0", "configuration_id": "cc-MODE0"},
            }
        )

    def test_incremental_baseline_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_baseline({"base_commit": "C0", "baseline": {"commit": "C1"}})


if __name__ == "__main__":
    unittest.main()
