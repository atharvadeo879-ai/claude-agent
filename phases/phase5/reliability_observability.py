"""Phase 5: retry policies and metrics."""

from dataclasses import dataclass
from time import perf_counter


@dataclass
class MetricsCollector:
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0

    def record(self, is_success: bool, latency_ms: float) -> None:
        if is_success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_latency_ms += max(latency_ms, 0.0)


class RetryExecutor:
    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max(max_attempts, 1)

    def run(self, fn):
        last_error = None
        for _ in range(self.max_attempts):
            started = perf_counter()
            try:
                result = fn()
                elapsed_ms = (perf_counter() - started) * 1000
                return result, elapsed_ms
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise RuntimeError("operation failed after retries") from last_error

