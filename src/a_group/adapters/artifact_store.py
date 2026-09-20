from typing import Protocol


class ArtifactStore(Protocol):
    def put(self, content: bytes, uri: str, media_type: str) -> str:
        """Persist content and return its readable artifact URI."""

    def get(self, uri: str) -> bytes:
        """Read content by artifact URI."""
