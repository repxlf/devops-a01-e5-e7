"""Job orchestration port; transport and persistence stay outside this module."""

from typing import Any, Mapping, Protocol


class JobRunner(Protocol):
    def submit(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        """Accept a request and return a 202-style job reference."""

    def get(self, job_id: str) -> Mapping[str, Any]:
        """Return the current canonical job view."""
