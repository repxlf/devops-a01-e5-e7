from typing import Protocol


class RepositoryReader(Protocol):
    def checkout(self, repository_url: str, commit: str, destination: str) -> None:
        """Materialize one immutable repository commit."""
