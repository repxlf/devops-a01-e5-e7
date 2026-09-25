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
            shutil.copytree(child, target, dirs_exist_ok=True)
        else:
            shutil.copy2(child, target)


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


def environment_record() -> dict[str, Any]:
    return {
        "provenance": "MOCK_FIXTURE",
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


def write_graph_and_reports(
    project: Path,
    destination: Path,
    commit: str,
    configuration_id: str,
    report_prefix: str,
) -> dict[str, Any]:
    actual = collect_dependency_graph(project, commit, configuration_id, "ACTUAL", f"actual-{report_prefix}")
    declared = collect_dependency_graph(project, commit, configuration_id, "DECLARED", f"declared-{report_prefix}")
    findings = detect_md_rd(actual, declared, commit)
    md_findings = [item for item in findings if item["type"] == "MISSING"]
    rd_findings = [item for item in findings if item["type"] == "REDUNDANT"]
    write_json(destination / "graphs" / f"actual-{report_prefix}.json", actual)
    write_json(destination / "graphs" / f"declared-{report_prefix}.json", declared)
    write_json(destination / "reports" / f"md-report-{report_prefix}.json", build_report("MD_REPORT", commit, configuration_id, md_findings))
    write_json(destination / "reports" / f"rd-report-{report_prefix}.json", build_report("RD_REPORT", commit, configuration_id, rd_findings))
    return {"actual": actual, "declared": declared, "findings": findings}


def run_md_rd_experiment(run_dir: Path, dry_run: bool, trace_dir: Path | None) -> dict[str, Any]:
    project = run_dir / "projects" / "md-rd"
    copy_fixture(FIXTURES / "md-rd", project)
    graph_result = write_graph_and_reports(project, run_dir, "fixture-md-rd", "cc-MODE0", "md-rd")
    build_result = run_build_sequence(project, "1", dry_run, trace_dir=trace_dir, trace_name="md-rd")
    return {"project": "md-rd", "graph": graph_result, "build": build_result}


def run_commit_experiment(run_dir: Path, dry_run: bool, trace_dir: Path | None) -> dict[str, Any]:
    expected = json.loads((FIXTURES / "commits" / "expected-observations.json").read_text(encoding="utf-8"))
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
                source = project / "main.c"
                object_file = project / "main.o"
                newer_than = max(time.time(), object_file.stat().st_mtime + 2) if object_file.exists() else time.time()
                os.utime(source, (newer_than, newer_than))
                commands.append({
                    "action": "normalize_mtime",
                    "path": str(source),
                    "reason": "C1 source changed; make must observe the change",
                })
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
        graph_result = write_graph_and_reports(project if not dry_run else FIXTURES / "commits" / commit, run_dir, snapshots[commit], "cc-MODE0", commit.lower())
        active_project = project if not dry_run else FIXTURES / "commits" / commit
        if commit == "C0":
            incremental_build = run_build_sequence(active_project, expected[commit]["expected_incremental_stdout"], dry_run, trace_dir=trace_dir, trace_name=f"{commit.lower()}-incremental")
            clean_build = incremental_build
        else:
            incremental_build = run_build_sequence(active_project, expected[commit]["expected_incremental_stdout"], dry_run, clean_first=False, trace_dir=trace_dir, trace_name=f"{commit.lower()}-incremental")
            clean_build = run_build_sequence(active_project, expected[commit]["expected_clean_stdout"], dry_run, clean_first=True, trace_dir=trace_dir, trace_name=f"{commit.lower()}-clean")
        results[commit] = {
            "commit": snapshots[commit],
            "expected": expected[commit],
            "graph": graph_result,
            "incremental_build": incremental_build,
            "clean_build": clean_build,
        }

    write_json(run_dir / "commands" / "commit-repository.json", commands)
    return {"snapshots": snapshots, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="directory for this run; defaults to work/e3-<UTC timestamp>")
    parser.add_argument("--dry-run", action="store_true", help="write the plan and fixture-derived graphs without executing tools")
    parser.add_argument("--strace", action="store_true", help="wrap make commands with Linux strace when it is available")
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = (args.output_dir or ROOT / "work" / f"e3-{timestamp}").resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    trace_dir = run_dir / "traces" if args.strace else None
    write_json(run_dir / "environment.json", environment_record())
    md_rd = run_md_rd_experiment(run_dir, args.dry_run, trace_dir)
    commits = run_commit_experiment(run_dir, args.dry_run, trace_dir)
    manifest = {
        "provenance": "MOCK_FIXTURE",
        "experiment": "E3_A01_PARALLEL_TEST_BASELINE",
        "dry_run": args.dry_run,
        "strace_requested": args.strace,
        "strace_available": shutil.which("strace") is not None,
        "run_dir": str(run_dir),
        "source": "fixtures/e3",
        "md_rd": {"build": md_rd["build"], "finding_count": len(md_rd["graph"]["findings"])},
        "commits": commits,
        "note": "Replace fixture source and rerun on the required Linux environment before labeling evidence as REAL_TOOL_OUTPUT.",
    }
    write_json(run_dir / "observations.json", manifest)
    print(json.dumps({"run_dir": str(run_dir), "provenance": "MOCK_FIXTURE", "dry_run": args.dry_run}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
