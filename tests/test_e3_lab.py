import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
E3_FIXTURES = ROOT / "fixtures" / "e3"


class E3LabTests(unittest.TestCase):
    def test_md_rd_fixture_produces_the_two_expected_findings(self) -> None:
        from a_group.e3.lab import collect_dependency_graph, detect_md_rd

        project = E3_FIXTURES / "md-rd"
        actual = collect_dependency_graph(
            project, "fixture-md-rd", "cc-MODE0", "ACTUAL", "actual-md-rd"
        )
        declared = collect_dependency_graph(
            project, "fixture-md-rd", "cc-MODE0", "DECLARED", "declared-md-rd"
        )
        findings = detect_md_rd(actual, declared, "fixture-md-rd")

        self.assertEqual(
            {(item["type"], item["target"], item["dependency"]) for item in findings},
            {
                ("MISSING", "main.o", "config.h"),
                ("REDUNDANT", "main.o", "unused.h"),
            },
        )
        self.assertTrue(all(item["evidence"] for item in findings))

    def test_commit_fixtures_capture_c0_c1_c2_expected_changes(self) -> None:
        from a_group.e3.lab import collect_dependency_graph, detect_md_rd

        expected = json.loads(
            (E3_FIXTURES / "commits" / "expected-observations.json").read_text(
                encoding="utf-8"
            )
        )
        for commit in ("C0", "C1", "C2"):
            project = E3_FIXTURES / "commits" / commit
            actual = collect_dependency_graph(project, commit, "cc-MODE0", "ACTUAL", f"actual-{commit}")
            declared = collect_dependency_graph(
                project, commit, "cc-MODE0", "DECLARED", f"declared-{commit}"
            )
            findings = detect_md_rd(actual, declared, commit)
            observed = sorted(
                (item["type"], item["target"], item["dependency"]) for item in findings
            )
            self.assertEqual(observed, sorted(map(tuple, expected[commit]["findings"])))

    def test_command_observation_preserves_exit_code_and_output(self) -> None:
        from a_group.e3.lab import run_command

        observation = run_command(
            [sys.executable, "-c", "print('e3-observation')"], ROOT
        )

        self.assertEqual(observation["returncode"], 0)
        self.assertIn("e3-observation", observation["stdout"])
        self.assertEqual(observation["stderr"], "")
        self.assertGreaterEqual(observation["duration_ms"], 0)

    def test_report_marks_fixture_provenance_until_linux_run_is_performed(self) -> None:
        from a_group.e3.lab import build_report

        report = build_report(
            "MD_REPORT",
            "fixture-md-rd",
            "cc-MODE0",
            [
                {
                    "finding_id": "finding-1",
                    "type": "MISSING",
                    "target": "main.o",
                    "dependency": "config.h",
                    "commit": "fixture-md-rd",
                    "detector": "A01_E3_MD_RD",
                    "evidence": ["source:main.c:include:config.h"],
                }
            ],
        )

        self.assertEqual(report["provenance"], "MOCK_FIXTURE")
        self.assertEqual(report["report_type"], "MD_REPORT")


if __name__ == "__main__":
    unittest.main()
