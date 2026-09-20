from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkResult:
    incremental_duration_ms: int
    full_duration_ms: int

    @property
    def speedup_ratio(self) -> float:
        if self.incremental_duration_ms == 0:
            return 0.0
        return self.full_duration_ms / self.incremental_duration_ms
