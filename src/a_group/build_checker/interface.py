"""Interfaces for the future BuildChecker implementation."""

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class FullCheckContext:
    repository_url: str
    commit: str
    configuration_id: str
    project_root: str
    clean_command: str
    build_command: str
    image: str | None = None


class BuildChecker(Protocol):
    """Run a full dependency check for one fixed commit and configuration."""

    def run(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        ...
