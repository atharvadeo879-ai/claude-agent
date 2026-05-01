import unittest

from phases.phase5 import MetricsCollector, RetryExecutor


class TestPhase5(unittest.TestCase):
    def test_retry_executor_eventually_succeeds(self):
        attempts = {"count": 0}

        def flaky():
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise ValueError("try again")
            return "ok"

        executor = RetryExecutor(max_attempts=2)
        result, latency_ms = executor.run(flaky)
        self.assertEqual(result, "ok")
        self.assertGreaterEqual(latency_ms, 0.0)

    def test_metrics_collector(self):
        metrics = MetricsCollector()
        metrics.record(True, 12.2)
        metrics.record(False, 5.8)
        self.assertEqual(metrics.success_count, 1)
        self.assertEqual(metrics.failure_count, 1)
        self.assertAlmostEqual(metrics.total_latency_ms, 18.0, places=1)


if __name__ == "__main__":
    unittest.main()

