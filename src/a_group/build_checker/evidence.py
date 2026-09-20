"""Evidence-generation port for BuildChecker findings."""

from typing import Any, Mapping, Protocol, Sequence


class EvidenceProvider(Protocol):
    def explain(
        self,
        finding: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> Sequence[str]:
        """Return evidence references tied to files, locations and commits."""


class UnimplementedEvidenceProvider:
    def explain(
        self,
        finding: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> Sequence[str]:
        raise NotImplementedError("Connect an evidence provider")
