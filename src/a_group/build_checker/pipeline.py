"""Composition point for a real BuildChecker implementation."""

from typing import Any, Mapping

from .evidence import EvidenceProvider
from .graph_collection import ActualGraphCollector, DeclaredGraphProvider
from .md_rd_detection import MdRdDetector


class BuildCheckerPipeline:
    def __init__(
        self,
        actual_graph_collector: ActualGraphCollector,
        declared_graph_provider: DeclaredGraphProvider,
        detector: MdRdDetector,
        evidence_provider: EvidenceProvider,
    ) -> None:
        self.actual_graph_collector = actual_graph_collector
        self.declared_graph_provider = declared_graph_provider
        self.detector = detector
        self.evidence_provider = evidence_provider

    def run(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        """Run the future full-check stages once concrete ports are available."""
        raise NotImplementedError(
            "Compose concrete repository, build, graph, detector and evidence adapters"
        )
