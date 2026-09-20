"""Composition point for a real EChecker implementation."""

from typing import Any, Mapping

from .incremental_update import IncrementalGraphUpdater


class ECheckerPipeline:
    def __init__(self, graph_updater: IncrementalGraphUpdater) -> None:
        self.graph_updater = graph_updater

    def run(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        """Run baseline validation, graph update and finding diff in the future."""
        raise NotImplementedError("Compose the concrete incremental graph and finding adapters")
