"""Dependency-free E3 laboratory primitives.

The functions in this module deliberately cover only the small experiment
described by the E3 material: local C includes, GNU Make prerequisites,
MISSING/REDUNDANT comparison, and observable command execution. They are not a
general C dependency analyzer and they do not replace BuildChecker adapters.
"""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping, Sequence


_INCLUDE_RE = re.compile(r'^\s*#\s*include\s*(?P<delimiter>["<])(?P<name>[^">]+)[">]')
_TARGET_RE = re.compile(r"^\s*([A-Za-z0-9_./-]+)\s*:\s*(.*?)\s*$")


def _normalise(value: str) -> str:
    return value.replace("\\", "/")


def _local_includes(source: Path) -> list[tuple[str, int]]:
    includes: list[tuple[str, int]] = []
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        match = _INCLUDE_RE.match(line)
        if match and match.group("delimiter") == '"':
            includes.append((match.group("name"), line_number))
    return includes


def _declared_edges(makefile: Path) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for line_number, line in enumerate(makefile.read_text(encoding="utf-8").splitlines(), 1):
        match = _TARGET_RE.match(line)
        if not match or match.group(1).startswith("."):
            continue
        target, prerequisites = match.groups()
        for dependency in prerequisites.split():
            if dependency.startswith("$") or dependency in {"|"}:
                continue
            edges.append(
                {
                    "source": _normalise(target),
                    "target": _normalise(dependency),
                    "evidence": f"Makefile:{line_number}:{target}:{dependency}",
                }
            )
    return edges


def collect_dependency_graph(
    project_root: Path,
    commit: str,
    configuration_id: str,
    graph_kind: str,
    graph_id: str,
    provenance: str = "MOCK_FIXTURE",
) -> dict[str, Any]:
    """Collect the deliberately narrow graph used by the E3 fixture.

    ACTUAL edges contain source-to-object edges and local quoted includes.
    DECLARED edges come from Makefile prerequisites. System headers are kept
    out of the graph because the E3 oracle concerns project-local files.
    """

    project_root = Path(project_root)
    declared_edges = _declared_edges(project_root / "Makefile")
    actual_edges: list[dict[str, str]] = []
    actual_nodes: set[str] = set()
    for source in sorted(project_root.glob("*.c")):
        object_file = f"{source.stem}.o"
        source_name = source.name
        actual_nodes.update({object_file, source_name})
        actual_edges.append(
            {
                "source": object_file,
                "target": source_name,
                "evidence": f"build:{object_file}:source:{source_name}",
            }
        )
        for dependency, line_number in _local_includes(source):
            actual_nodes.add(dependency)
            actual_edges.append(
                {
                    "source": object_file,
                    "target": dependency,
                    "evidence": f"source:{source_name}:include:{dependency}:line:{line_number}",
                }
            )

    # The fixture's link step is observable from the Makefile recipe. Keep
    # object-to-header analysis driven by source includes, while retaining the
    # executable-to-object edge that the link command consumes.
    for edge in declared_edges:
        if not edge["source"].endswith(".o") and edge["target"].endswith(".o"):
            actual_nodes.update({edge["source"], edge["target"]})
            actual_edges.append(
                {
                    "source": edge["source"],
                    "target": edge["target"],
                    "evidence": f"build:{edge['source']}:link:{edge['target']}",
                }
            )
    declared_nodes: set[str] = set()
    for edge in declared_edges:
        declared_nodes.update({edge["source"], edge["target"]})

    if graph_kind == "ACTUAL":
        edges = actual_edges
        nodes = actual_nodes
    elif graph_kind == "DECLARED":
        edges = declared_edges
        nodes = declared_nodes
    else:
        raise ValueError(f"Unsupported graph kind: {graph_kind}")

    return {
        "graph_id": graph_id,
        "graph_kind": graph_kind,
        "commit": commit,
        "configuration_id": configuration_id,
        "nodes": sorted(nodes),
        "edges": sorted(edges, key=lambda item: (item["source"], item["target"])),
        "provenance": provenance,
    }


def _edge_key(edge: Mapping[str, Any]) -> tuple[str, str]:
    return str(edge.get("source", "")), str(edge.get("target", ""))


def detect_md_rd(
    actual_graph: Mapping[str, Any],
    declared_graph: Mapping[str, Any],
    commit: str,
    detector: str = "A01_E3_MD_RD",
    provenance: str = "MOCK_FIXTURE",
) -> list[dict[str, Any]]:
    """Compare graph edges and return traceable MISSING/REDUNDANT findings."""

    actual = {_edge_key(edge): edge for edge in actual_graph.get("edges", [])}
    declared = {_edge_key(edge): edge for edge in declared_graph.get("edges", [])}
    findings: list[dict[str, Any]] = []

    for kind, edges, other in (
        ("MISSING", actual, declared),
        ("REDUNDANT", declared, actual),
    ):
        for (target, dependency), edge in sorted(edges.items()):
            if (target, dependency) in other:
                continue
            finding_id = f"{kind.lower()}-{commit}-{target}-{dependency}".replace("/", "_")
            evidence = [str(edge.get("evidence", ""))]
            findings.append(
                {
                    "finding_id": finding_id,
                    "type": kind,
                    "target": target,
                    "dependency": dependency,
                    "commit": commit,
                    "detector": detector,
                    "location": {"artifact": edge.get("evidence", "")},
                    "evidence": evidence,
                    "provenance": provenance,
                }
            )
    return findings


def build_report(
    report_type: str,
    commit: str,
    configuration_id: str,
    findings: Sequence[Mapping[str, Any]],
    provenance: str = "MOCK_FIXTURE",
) -> dict[str, Any]:
    """Build an MD/RD report with an explicit provenance marker."""

    return {
        "report_type": report_type,
        "report_id": f"{report_type.lower()}-{commit}",
        "commit": commit,
        "configuration_id": configuration_id,
        "findings": [dict(item) for item in findings],
        "provenance": provenance,
    }


def run_command(
    command: Sequence[str],
    cwd: Path,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    """Execute one observable lab command and preserve its result."""

    started = time.perf_counter()
    timed_out = False
    try:
        result = subprocess.run(
            list(command),
            cwd=Path(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        returncode = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        returncode = 124
        stdout = error.stdout or ""
        stderr = error.stderr or ""
    except OSError as error:
        returncode = 127
        stdout = ""
        stderr = str(error)
    duration_ms = int((time.perf_counter() - started) * 1000)
    return {
        "command": [str(item) for item in command],
        "cwd": str(Path(cwd)),
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "duration_ms": duration_ms,
        "timed_out": timed_out,
    }
