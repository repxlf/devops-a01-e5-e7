"""Ports for comparing actual and declared dependency graphs."""

from typing import Any, Mapping, Protocol, Sequence


class MdRdDetector(Protocol):
    def detect(
        self,
        actual_graph: Mapping[str, Any],
        declared_graph: Mapping[str, Any],
    ) -> Sequence[Mapping[str, Any]]:
        """Return MISSING/REDUNDANT findings for one configuration."""


class UnimplementedMdRdDetector:
    def detect(
        self,
        actual_graph: Mapping[str, Any],
        declared_graph: Mapping[str, Any],
    ) -> Sequence[Mapping[str, Any]]:
        raise NotImplementedError("Implement or connect the MD/RD detector")
