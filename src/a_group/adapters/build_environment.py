from typing import Mapping, Protocol, Any


class BuildEnvironment(Protocol):
    def run(self, context: Mapping[str, Any]) -> Mapping[str, Any]:
        """Run clean/build/verify commands and return logs plus exit state."""
