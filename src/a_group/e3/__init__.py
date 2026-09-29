"""Small, replaceable helpers for the E3 A-group laboratory."""

from .lab import (
    build_report,
    collect_dependency_graph,
    detect_md_rd,
    run_command,
)

__all__ = [
    "build_report",
    "collect_dependency_graph",
    "detect_md_rd",
    "run_command",
]
