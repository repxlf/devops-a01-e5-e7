"""Small dependency-free models for contract-facing code.

These models deliberately do not implement dependency analysis. They give
future adapters and service implementations a stable vocabulary while the
JSON files under schemas/ remain the interchange contract.
"""

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    type: str
    uri: str
    media_type: str
    producer_job_id: str
    sha256: str | None = None


@dataclass(frozen=True)
class Finding:
    finding_id: str
    type: str
    target: str
    dependency: str
    commit: str
    detector: str
    location: Mapping[str, Any] = field(default_factory=dict)
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class JobError:
    code: str
    message: str
    retryable: bool = False


@dataclass
class Job:
    schema_version: str
    job_id: str
    trace_id: str
    job_type: str
    status: str
    input: dict[str, Any]
    output: dict[str, Any] | None = None
    error: JobError | None = None
    execution: dict[str, Any] = field(default_factory=dict)

    @property
    def has_analysis_findings(self) -> bool:
        if not self.output:
            return False
        return bool(
            self.output.get("findings")
            or self.output.get("added_findings")
            or self.output.get("resolved_findings")
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Job":
        raw_error = value.get("error")
        error = JobError(**raw_error) if isinstance(raw_error, Mapping) else None
        return cls(
            schema_version=str(value["schema_version"]),
            job_id=str(value["job_id"]),
            trace_id=str(value["trace_id"]),
            job_type=str(value["job_type"]),
            status=str(value["status"]),
            input=dict(value.get("input", {})),
            output=dict(value["output"]) if isinstance(value.get("output"), Mapping) else None,
            error=error,
            execution=dict(value.get("execution", {})),
        )
