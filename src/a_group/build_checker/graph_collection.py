"""Ports for collecting actual and declared dependency graphs."""

from typing import Any, Mapping, Protocol


class ActualGraphCollector(Protocol):
    def collect_actual(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        """Collect the graph observed from a completed build."""


class DeclaredGraphProvider(Protocol):
    def load_declared(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        """Load the graph declared by project configuration."""


class UnimplementedGraphCollector:
    """Explicit placeholder until a real build/graph tool is selected."""

    def collect_actual(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError("Connect an actual dependency graph collector")


class UnimplementedDeclaredGraphProvider:
    def load_declared(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError("Connect a declared dependency graph provider")
