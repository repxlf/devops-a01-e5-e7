"""Interfaces for the future EChecker implementation."""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class IncrementalCheckContext:
    base_commit: str
    current_commit: str
    baseline_graph_uri: str
    baseline_configuration_id: str
    current_configuration_id: str


class EChecker(Protocol):
    """Run an incremental check from one baseline to one current commit."""

    def run(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        ...
