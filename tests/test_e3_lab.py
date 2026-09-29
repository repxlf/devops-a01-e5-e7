import json
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
E3_FIXTURES = ROOT / "fixtures" / "e3"
sys.path.insert(0, str(ROOT / "src"))


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

    def test_instructor_oracle_is_separate_from_generated_results(self) -> None:
        oracle = json.loads(
            (E3_FIXTURES / "instructor-oracle.json").read_text(encoding="utf-8")
        )
        expected = json.loads(
            (E3_FIXTURES / "commits" / "expected-observations.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual("INSTRUCTOR_ORACLE", oracle["provenance"])
        self.assertEqual("MOCK_FIXTURE", expected["provenance"])
        self.assertEqual("cc-O0-MODE0", expected["C1"]["configuration_id"])
        self.assertEqual("cc-O0-MODE7", expected["C2"]["configuration_id"])
        self.assertEqual(oracle["commits"]["C2"], expected["C2"])

    def test_dry_run_is_a_plan_not_verified_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="a01-e3-plan-") as temporary:
            output = Path(temporary) / "plan"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_lab.py"),
                    "--dry-run",
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            observations = json.loads(
                (output / "observations.json").read_text(encoding="utf-8")
            )
            self.assertEqual("PLANNED", observations["status"])
            self.assertFalse(observations["verified"])
            self.assertEqual("MOCK_FIXTURE", observations["provenance"])

    @unittest.skipUnless(
        platform.system() == "Linux"
        and all(shutil.which(name) for name in ("git", "make", "cc", "strace")),
        "the verified E3 runner requires Linux, git, make, cc and strace",
    )
    def test_real_runner_covers_all_required_a_group_behaviours(self) -> None:
        with tempfile.TemporaryDirectory(prefix="a01-e3-test-") as temporary:
            output = Path(temporary) / "run"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_lab.py"),
                    "--strace",
                    "--output-dir",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            observations = json.loads(
                (output / "observations.json").read_text(encoding="utf-8")
            )
            self.assertEqual("PASSED", observations["status"])
            self.assertTrue(observations["verified"])

            md_rd = observations["md_rd"]
            self.assertEqual("1", md_rd["initial_build"]["actual_stdout"])
            self.assertEqual(
                "1", md_rd["after_config_change_incremental"]["actual_stdout"]
            )
            self.assertEqual("2", md_rd["after_config_change_clean"]["actual_stdout"])
            self.assertEqual(
                "2", md_rd["after_unused_change_incremental"]["actual_stdout"]
            )
            self.assertTrue(md_rd["unused_change_recompiled_main_o"])
            self.assertTrue(md_rd["findings_match_oracle"])

            commits = observations["commits"]
            self.assertTrue(commits["fixture_matches_oracle"])
            self.assertTrue(commits["c1_c2_command_changed"])
            self.assertEqual(3, len(set(commits["snapshots"].values())))
            self.assertEqual("12", commits["results"]["C2"]["incremental_build"]["actual_stdout"])
            self.assertEqual("19", commits["results"]["C2"]["clean_build"]["actual_stdout"])
            tags = subprocess.run(
                ["git", "-C", str(output / "projects" / "commits"), "tag", "--list"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.splitlines()
            self.assertEqual(["C0", "C1", "C2"], tags)
            self.assertTrue((output / "commands.json").exists())

            commands = json.loads((output / "commands.json").read_text(encoding="utf-8"))
            stderr = "\n".join(str(item.get("stderr", "")) for item in commands)
            self.assertNotIn("Clock skew detected", stderr)


if __name__ == "__main__":
    unittest.main()
