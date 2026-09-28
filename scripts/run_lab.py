#!/usr/bin/env python3
"""Run the A-group E3 laboratory and preserve its observations.

The default mode executes the supplied fixture with local tools and writes a
new work directory. ``--dry-run`` records the experiment plan without claiming
that a build or Linux trace happened.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "e3"
sys.path.insert(0, str(ROOT / "src"))

from a_group.e3.lab import (  # noqa: E402
    build_report,
    collect_dependency_graph,
    detect_md_rd,
    run_command,
)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_fixture(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir():
            shutil.copytree(child, target, dirs_exist_ok=True, copy_function=shutil.copy)
        else:
            # Do not preserve timestamps from a Windows mount or archive.  Make's
            # incremental behaviour is the subject of this experiment, so every
            # run must start with timestamps created on the executing filesystem.
            shutil.copy(child, target)


def tool_info(name: str) -> dict[str, Any]:
    executable = shutil.which(name)
    if not executable:
        return {"name": name, "available": False, "executable": None, "version": None}
    result = run_command([executable, "--version"], ROOT)
    return {
        "name": name,
        "available": result["returncode"] == 0,
        "executable": executable,
        "version": result["stdout"].splitlines()[0] if result["stdout"] else result["stderr"].splitlines()[0] if result["stderr"] else None,
    }


def environment_record(provenance: str) -> dict[str, Any]:
    return {
        "provenance": provenance,
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "python": sys.version,
        "tools": [tool_info(name) for name in ("git", "make", "mingw32-make", "cc", "gcc", "strace")],
    }


def planned_command(command: Iterable[str], cwd: Path) -> dict[str, Any]:
    return {
        "command": [str(item) for item in command],
        "cwd": str(cwd),
        "status": "SKIPPED",
        "reason": "dry-run; no command was executed",
    }


def run_or_plan(command: list[str], cwd: Path, dry_run: bool, commands: list[dict[str, Any]]) -> dict[str, Any]:
    if dry_run:
        observation = planned_command(command, cwd)
    else:
        observation = run_command(command, cwd)
    commands.append(observation)
    return observation


def executable_command(project: Path) -> list[str]:
    if os.name == "nt":
        return [str(project / "app.exe")]
    return [str(project / "app")]


def make_command(
    make: str,
    arguments: list[str],
    trace_dir: Path | None,
    trace_name: str,
) -> list[str]:
    command = [make, *arguments]
    strace = shutil.which("strace")
    if trace_dir and strace:
        trace_dir.mkdir(parents=True, exist_ok=True)
        return [strace, "-ff", "-o", str(trace_dir / trace_name), "-e", "trace=%file,%process", *command]
    return command


def run_build_sequence(
    project: Path,
    expected_stdout: str,
    dry_run: bool,
    clean_first: bool = True,
    trace_dir: Path | None = None,
    trace_name: str = "make",
) -> dict[str, Any]:
    commands: list[dict[str, Any]] = []
    make = shutil.which("make") or shutil.which("mingw32-make") or "make"
    clean = None
    if clean_first:
        clean = run_or_plan(make_command(make, ["clean"], trace_dir, f"{trace_name}-clean"), project, dry_run, commands)
    build = run_or_plan(make_command(make, [], trace_dir, f"{trace_name}-build"), project, dry_run, commands)
    execute = run_or_plan(executable_command(project), project, dry_run, commands)
    actual_stdout = "" if dry_run else execute.get("stdout", "").strip()
    stdout_matches = dry_run or actual_stdout == expected_stdout
    return {
        "expected_stdout": expected_stdout,
        "actual_stdout": actual_stdout,
        "clean_returncode": None if clean is None else clean.get("returncode"),
        "build_returncode": build.get("returncode"),
        "execute_returncode": execute.get("returncode"),
        "stdout_matches_expected": stdout_matches,
        "success": (dry_run or ((not clean_first or clean.get("returncode") == 0) and build.get("returncode") == 0 and execute.get("returncode") == 0 and stdout_matches)),
        "commands": commands,
    }


def record_file_change(path: Path, new_content: str, reason: str) -> dict[str, Any]:
    """Apply and record an intentional fixture mutation."""

    before = path.read_text(encoding="utf-8")
    path.write_text(new_content, encoding="utf-8")
    return {
        "action": "write_file",
        "path": str(path),
        "reason": reason,
        "before": before,
        "after": new_content,
    }


def make_newer_than(
    path: Path,
    reference: Path,
    reason: str,
    unchanged_inputs: Iterable[Path] = (),
) -> dict[str, Any]:
    """Make a changed input observably newer than an existing build product."""

    now = time.time()
    original_reference_mtime = reference.stat().st_mtime if reference.exists() else None
    normalized_reference_mtime = None
    if reference.exists():
        normalized_reference_mtime = now - 2
        os.utime(reference, (normalized_reference_mtime, normalized_reference_mtime))
    normalized_inputs: list[str] = []
    for unchanged in unchanged_inputs:
        if unchanged.exists():
            os.utime(unchanged, (now - 4, now - 4))
            normalized_inputs.append(str(unchanged))
    timestamp = now
    os.utime(path, (timestamp, timestamp))
    return {
        "action": "normalize_mtime",
        "path": str(path),
        "reference": str(reference),
        "mtime": timestamp,
        "reference_mtime_before": original_reference_mtime,
        "reference_mtime_after": normalized_reference_mtime,
        "unchanged_inputs_made_older": normalized_inputs,
        "reason": reason,
    }


def finding_keys(findings: Iterable[dict[str, Any]]) -> list[list[str]]:
    return sorted(
        [[str(item["type"]), str(item["target"]), str(item["dependency"])] for item in findings]
    )


def write_graph_and_reports(
    project: Path,
    destination: Path,
    commit: str,
    configuration_id: str,
    report_prefix: str,
    provenance: str,
) -> dict[str, Any]:
    actual = collect_dependency_graph(project, commit, configuration_id, "ACTUAL", f"actual-{report_prefix}", provenance)
    declared = collect_dependency_graph(project, commit, configuration_id, "DECLARED", f"declared-{report_prefix}", provenance)
    findings = detect_md_rd(actual, declared, commit, provenance=provenance)
    md_findings = [item for item in findings if item["type"] == "MISSING"]
    rd_findings = [item for item in findings if item["type"] == "REDUNDANT"]
    write_json(destination / "graphs" / f"actual-{report_prefix}.json", actual)
    write_json(destination / "graphs" / f"declared-{report_prefix}.json", declared)
    write_json(destination / "reports" / f"md-report-{report_prefix}.json", build_report("MD_REPORT", commit, configuration_id, md_findings, provenance))
    write_json(destination / "reports" / f"rd-report-{report_prefix}.json", build_report("RD_REPORT", commit, configuration_id, rd_findings, provenance))
    return {"actual": actual, "declared": declared, "findings": findings}


def run_md_rd_experiment(
    run_dir: Path,
    dry_run: bool,
    trace_dir: Path | None,
    provenance: str,
    oracle: dict[str, Any],
) -> dict[str, Any]:
    project = run_dir / "projects" / "md-rd"
    copy_fixture(FIXTURES / "md-rd", project)
    graph_result = write_graph_and_reports(project, run_dir, "fixture-md-rd", "cc-MODE0", "md-rd", provenance)
    expected = oracle["md_rd"]
    commands: list[dict[str, Any]] = []

    initial = run_build_sequence(
        project,
        expected["initial_stdout"],
        dry_run,
        trace_dir=trace_dir,
        trace_name="md-rd-initial",
    )
    commands.extend(initial["commands"])

    if dry_run:
        config_change = {
            "action": "write_file",
            "path": str(project / "config.h"),
            "status": "SKIPPED",
            "reason": "dry-run; would change VALUE from 1 to 2",
        }
        config_mtime = {
            "action": "normalize_mtime",
            "path": str(project / "config.h"),
            "status": "SKIPPED",
            "reason": "dry-run; would make config.h newer than main.o",
        }
    else:
        config_change = record_file_change(
            project / "config.h",
            "#define VALUE 2\n",
            "E3 MD behaviour: change only the undeclared header",
        )
        config_mtime = make_newer_than(
            project / "config.h",
            project / "main.o",
            "ensure make observes config.h as changed after the initial build",
            (project / "main.c", project / "unused.h"),
        )
    commands.extend([config_change, config_mtime])

    after_config_incremental = run_build_sequence(
        project,
        expected["after_config_change_incremental_stdout"],
        dry_run,
        clean_first=False,
        trace_dir=trace_dir,
        trace_name="md-rd-after-config-incremental",
    )
    commands.extend(after_config_incremental["commands"])
    after_config_clean = run_build_sequence(
        project,
        expected["after_config_change_clean_stdout"],
        dry_run,
        trace_dir=trace_dir,
        trace_name="md-rd-after-config-clean",
    )
    commands.extend(after_config_clean["commands"])

    unused_path = project / "unused.h"
    if dry_run:
        unused_change = {
            "action": "write_file",
            "path": str(unused_path),
            "status": "SKIPPED",
            "reason": "dry-run; would change only the unused declared header",
        }
        unused_mtime = {
            "action": "normalize_mtime",
            "path": str(unused_path),
            "status": "SKIPPED",
            "reason": "dry-run; would make unused.h newer than main.o",
        }
    else:
        unused_change = record_file_change(
            unused_path,
            unused_path.read_text(encoding="utf-8") + "/* E3 RD behaviour change. */\n",
            "E3 RD behaviour: change only a declared but unused header",
        )
        unused_mtime = make_newer_than(
            unused_path,
            project / "main.o",
            "ensure make observes unused.h as changed after the clean build",
            (project / "main.c", project / "config.h"),
        )
    commands.extend([unused_change, unused_mtime])
    after_unused_incremental = run_build_sequence(
        project,
        expected["after_unused_change_stdout"],
        dry_run,
        clean_first=False,
        trace_dir=trace_dir,
        trace_name="md-rd-after-unused-incremental",
    )
    commands.extend(after_unused_incremental["commands"])
    build_stdout = after_unused_incremental["commands"][0].get("stdout", "")
    recompiled_main_o = dry_run or ("-c main.c" in build_stdout and "main.o" in build_stdout)
    findings_match = finding_keys(graph_result["findings"]) == sorted(expected["findings"])
    success = all(
        result["success"]
        for result in (initial, after_config_incremental, after_config_clean, after_unused_incremental)
    ) and recompiled_main_o and findings_match
    return {
        "project": "md-rd",
        "oracle": {"provenance": "INSTRUCTOR_ORACLE", "source": "fixtures/e3/instructor-oracle.json"},
        "graph": graph_result,
        "findings_match_oracle": findings_match,
        "initial_build": initial,
        "after_config_change_incremental": after_config_incremental,
        "after_config_change_clean": after_config_clean,
        "after_unused_change_incremental": after_unused_incremental,
        "unused_change_recompiled_main_o": recompiled_main_o,
        "success": success,
        "commands": commands,
    }


def run_commit_experiment(
    run_dir: Path,
    dry_run: bool,
    trace_dir: Path | None,
    provenance: str,
    oracle: dict[str, Any],
) -> dict[str, Any]:
    fixture_expected = json.loads(
        (FIXTURES / "commits" / "expected-observations.json").read_text(encoding="utf-8")
    )
    expected = oracle["commits"]
    fixture_matches_oracle = all(fixture_expected[name] == expected[name] for name in ("C0", "C1", "C2"))
    commands: list[dict[str, Any]] = []
    snapshots: dict[str, str] = {}
    project = run_dir / "projects" / "commits"

    if dry_run:
        snapshots = {commit: commit for commit in ("C0", "C1", "C2")}
    else:
        project.mkdir(parents=True, exist_ok=True)
        git = shutil.which("git") or "git"
        init = run_command([git, "init", str(project)], run_dir)
        commands.append(init)
        if init["returncode"] != 0:
            raise RuntimeError(f"git init failed: {init['stderr']}")
        for config in (("user.name", "E3 Lab Fixture"), ("user.email", "e3-lab@example.invalid")):
            commands.append(run_command([git, "-C", str(project), "config", *config], run_dir))
        for commit in ("C0", "C1", "C2"):
            copy_fixture(FIXTURES / "commits" / commit, project)
            commands.append(run_command([git, "-C", str(project), "add", "."], run_dir))
            commands.append(run_command([git, "-C", str(project), "commit", "-m", commit], run_dir))
            revision = run_command([git, "-C", str(project), "rev-parse", "HEAD"], run_dir)
            commands.append(revision)
            if revision["returncode"] != 0:
                raise RuntimeError(f"cannot resolve {commit}: {revision['stderr']}")
            snapshots[commit] = revision["stdout"].strip()
            tag = run_command([git, "-C", str(project), "tag", commit, snapshots[commit]], run_dir)
            commands.append(tag)
            if tag["returncode"] != 0:
                raise RuntimeError(f"cannot create tag {commit}: {tag['stderr']}")

    results: dict[str, Any] = {}
    for commit in ("C0", "C1", "C2"):
        if not dry_run:
            git = shutil.which("git") or "git"
            checkout = run_command([git, "-C", str(project), "checkout", "--quiet", snapshots[commit]], run_dir)
            commands.append(checkout)
            if checkout["returncode"] != 0:
                raise RuntimeError(f"checkout {commit} failed: {checkout['stderr']}")
            if commit == "C1":
                # Some filesystems give a freshly checked-out file the same
                # timestamp as main.o. Preserve the E3 intent that C1 changes
                # main.c and therefore triggers a normal incremental compile.
                commands.append(
                    make_newer_than(
                        project / "main.c",
                        project / "main.o",
                        "C1 source changed; make must observe the change",
                        (project / "config.h", project / "feature.h"),
                    )
                )
            if commit == "C2" and (project / "main.o").exists():
                # C2 changes only CFLAGS. Keep the C1 object and its input
                # headers older than it so normal make does not recompile.
                object_mtime = (project / "main.o").stat().st_mtime
                for name in ("main.c", "config.h", "feature.h"):
                    path = project / name
                    if path.exists():
                        old_mtime = min(path.stat().st_mtime, object_mtime - 2)
                        os.utime(path, (old_mtime, old_mtime))
                        commands.append({
                            "action": "normalize_mtime",
                            "path": str(path),
                            "reason": "C2 changes only CFLAGS; preserve C1 object for normal make",
                        })
        active_project = project if not dry_run else FIXTURES / "commits" / commit
        configuration_id = expected[commit]["configuration_id"]
        make = shutil.which("make") or shutil.which("mingw32-make") or "make"
        command_snapshot = run_or_plan(
            [make, "-n", "-B", "main.o"], active_project, dry_run, commands
        )
        graph_result = write_graph_and_reports(
            active_project,
            run_dir,
            snapshots[commit],
            configuration_id,
            commit.lower(),
            provenance,
        )
        if commit == "C0":
            incremental_build = run_build_sequence(active_project, expected[commit]["expected_incremental_stdout"], dry_run, trace_dir=trace_dir, trace_name=f"{commit.lower()}-incremental")
            clean_build = incremental_build
            commands.extend(incremental_build["commands"])
        else:
            incremental_build = run_build_sequence(active_project, expected[commit]["expected_incremental_stdout"], dry_run, clean_first=False, trace_dir=trace_dir, trace_name=f"{commit.lower()}-incremental")
            clean_build = run_build_sequence(active_project, expected[commit]["expected_clean_stdout"], dry_run, clean_first=True, trace_dir=trace_dir, trace_name=f"{commit.lower()}-clean")
            commands.extend(incremental_build["commands"])
            commands.extend(clean_build["commands"])
        results[commit] = {
            "commit": snapshots[commit],
            "tag": commit,
            "configuration_id": configuration_id,
            "expected": expected[commit],
            "command_snapshot": command_snapshot,
            "graph": graph_result,
            "findings_match_oracle": finding_keys(graph_result["findings"])
            == sorted(expected[commit]["findings"]),
            "incremental_build": incremental_build,
            "clean_build": clean_build,
        }

    write_json(run_dir / "commands" / "commit-repository.json", commands)
    command_changed_c1_c2 = (
        dry_run
        or results["C1"]["command_snapshot"].get("stdout")
        != results["C2"]["command_snapshot"].get("stdout")
    )
    success = (
        all(
            item["findings_match_oracle"]
            and item["incremental_build"]["success"]
            and item["clean_build"]["success"]
            and (dry_run or item["command_snapshot"].get("returncode") == 0)
            for item in results.values()
        )
        and command_changed_c1_c2
        and len(set(snapshots.values())) == 3
        and all(item.get("returncode", 0) == 0 for item in commands)
        and fixture_matches_oracle
    )
    return {
        "oracle": {"provenance": "INSTRUCTOR_ORACLE", "source": "fixtures/e3/instructor-oracle.json"},
        "snapshots": snapshots,
        "results": results,
        "c1_c2_command_changed": command_changed_c1_c2,
        "fixture_matches_oracle": fixture_matches_oracle,
        "success": success,
        "commands": commands,
    }


def trace_summary(trace_dir: Path | None) -> dict[str, Any]:
    if trace_dir is None:
        return {"enabled": False, "file_count": 0, "config_h_records": 0, "feature_h_records": 0}
    files = sorted(path for path in trace_dir.glob("*") if path.is_file())
    counts = {"config.h": 0, "feature.h": 0}
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in counts:
            counts[name] += sum(name in line for line in text.splitlines())
    return {
        "enabled": True,
        "file_count": len(files),
        "config_h_records": counts["config.h"],
        "feature_h_records": counts["feature.h"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="directory for this run; defaults to work/e3-<UTC timestamp>")
    parser.add_argument("--dry-run", action="store_true", help="write the plan and fixture-derived graphs without executing tools")
    parser.add_argument("--strace", action="store_true", help="wrap make commands with Linux strace when it is available")
    args = parser.parse_args()

    # dry-run 只写计划、不执行任何工具 → MOCK_FIXTURE
    # 真实运行由 make/cc/git 实际执行并保留观察记录（含失败）→ REAL_TOOL_OUTPUT
    provenance = "MOCK_FIXTURE" if args.dry_run else "REAL_TOOL_OUTPUT"

    if not args.dry_run:
        if platform.system() != "Linux":
            parser.error("a real E3 run requires Linux; use --dry-run on other systems")
        missing = [name for name in ("git", "cc") if shutil.which(name) is None]
        if shutil.which("make") is None and shutil.which("mingw32-make") is None:
            missing.append("make")
        if args.strace and shutil.which("strace") is None:
            missing.append("strace")
        if missing:
            parser.error(f"missing required tools for a real E3 run: {', '.join(missing)}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = (args.output_dir or ROOT / "work" / f"e3-{timestamp}").resolve()
    if run_dir.exists():
        parser.error(f"output directory already exists; choose a new directory: {run_dir}")
    run_dir.mkdir(parents=True)
    trace_dir = run_dir / "traces" if args.strace else None
    oracle = json.loads((FIXTURES / "instructor-oracle.json").read_text(encoding="utf-8"))
    write_json(run_dir / "environment.json", environment_record(provenance))
    md_rd = run_md_rd_experiment(run_dir, args.dry_run, trace_dir, provenance, oracle)
    commits = run_commit_experiment(run_dir, args.dry_run, trace_dir, provenance, oracle)
    traces = trace_summary(trace_dir)
    trace_success = not args.strace or (
        traces["file_count"] > 0
        and traces["config_h_records"] > 0
        and traces["feature_h_records"] > 0
    )
    checks_passed = md_rd["success"] and commits["success"] and trace_success
    verified = not args.dry_run and args.strace and checks_passed
    all_commands = [*md_rd["commands"], *commits["commands"]]
    write_json(run_dir / "commands.json", all_commands)
    manifest = {
        "provenance": provenance,
        "experiment": "E3_A01_PARALLEL_TEST_BASELINE",
        "dry_run": args.dry_run,
        "strace_requested": args.strace,
        "strace_available": shutil.which("strace") is not None,
        "run_dir": str(run_dir),
        "source": "fixtures/e3",
        "oracle": {"provenance": oracle["provenance"], "source": "fixtures/e3/instructor-oracle.json"},
        "md_rd": md_rd,
        "commits": commits,
        "trace_summary": traces,
        "status": (
            "PLANNED"
            if args.dry_run
            else "PASSED"
            if verified
            else "PASSED_WITHOUT_TRACE"
            if checks_passed
            else "FAILED"
        ),
        "checks_passed": checks_passed,
        "verified": verified,
        "note": (
            "dry-run：只记录计划，未执行任何工具。"
            if args.dry_run
            else "真实运行：由 make/cc/git 实际执行产生，含命令退出码与输出；归档证据前请核对预期值。"
        ),
    }
    write_json(run_dir / "observations.json", manifest)
    print(json.dumps({"run_dir": str(run_dir), "provenance": provenance, "dry_run": args.dry_run, "status": manifest["status"], "verified": verified}, ensure_ascii=False))
    return 0 if args.dry_run or checks_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
