"""Port for updating a dependency graph from a baseline."""

from typing import Any, Mapping, Protocol


class IncrementalGraphUpdater(Protocol):
    def update(
        self,
        baseline_graph: Mapping[str, Any],
        current_context: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Produce the graph for the current commit."""


class UnimplementedIncrementalGraphUpdater:
    def update(
        self,
        baseline_graph: Mapping[str, Any],
        current_context: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        raise NotImplementedError("Implement the incremental graph updater")
