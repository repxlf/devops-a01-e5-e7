import unittest

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from a_group.e_checker.finding_diff import diff_findings
from a_group.evaluation.benchmark import BenchmarkResult
from a_group.evaluation.consistency import compare_graphs


class EvaluationTests(unittest.TestCase):
    def test_finding_diff_returns_added_and_resolved(self):
        added, resolved = diff_findings(
            [{"finding_id": "old"}],
            [{"finding_id": "new"}],
        )
        self.assertEqual(["new"], [item["finding_id"] for item in added])
        self.assertEqual(["old"], [item["finding_id"] for item in resolved])

    def test_graph_comparison_ignores_edge_order(self):
        left = {"edges": [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}]}
        right = {"edges": [{"source": "b", "target": "c"}, {"source": "a", "target": "b"}]}
        self.assertTrue(compare_graphs(left, right))

    def test_benchmark_reports_full_over_incremental_ratio(self):
        result = BenchmarkResult(incremental_duration_ms=5, full_duration_ms=20)
        self.assertEqual(4.0, result.speedup_ratio)


if __name__ == "__main__":
    unittest.main()
