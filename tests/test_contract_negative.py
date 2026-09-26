import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import validate

class TestContractNegativeCases(unittest.TestCase):

    def test_invalid_job_type_should_be_rejected(self):
        invalid_job = {
            "schema_version": "1.0.0",
            "job_id": "job-test-invalid-01",
            "trace_id": "trace-test-invalid-01",
            "job_type": "ABC",
            "status": "QUEUED",
            "input": {},
            "output": None,
            "error": None
        }
        with self.assertRaises(ValueError):
            validate.validate_job(invalid_job)

    def test_incremental_check_missing_baseline_should_be_rejected(self):
        missing_baseline_job = {
            "schema_version": "1.0.0",
            "job_id": "job-test-inc-invalid",
            "trace_id": "trace-test-inc-invalid",
            "job_type": "INCREMENTAL_CHECK",
            "status": "QUEUED",
            "input": {
                "base_commit": "0123456789abcdef0123456789abcdef01234567",
                "repository": {
                    "url": "https://git.nju.edu.cn/devops-a01/repo.git",
                    "commit": "abcdef0123456789abcdef0123456789abcdef01"
                }
            },
            "output": None,
            "error": None
        }
        with self.assertRaises(ValueError):
            validate.validate_job(missing_baseline_job)

if __name__ == "__main__":
    unittest.main()