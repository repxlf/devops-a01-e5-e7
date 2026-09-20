"""End-to-end composition point for DRAFT through RECHECK."""

from typing import Any, Mapping, Protocol


class StageRunner(Protocol):
    def run(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class EndToEndFlow:
    def __init__(self, stages: Mapping[str, StageRunner]) -> None:
        self.stages = dict(stages)

    def run(self, scenario: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError("Connect concrete stage runners for the end-to-end flow")
