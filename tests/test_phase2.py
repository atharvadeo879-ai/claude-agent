import unittest

from phases.phase2 import TokenUsageService


class TestPhase2(unittest.TestCase):
    def test_records_and_calculates_remaining_tokens(self):
        service = TokenUsageService(daily_limit=100)
        service.record_usage("u1", "2026-05-01", 20, 10)
        quota = service.get_daily_quota("u1", "2026-05-01")
        self.assertEqual(quota.used_today, 30)
        self.assertEqual(quota.remaining_today, 70)


if __name__ == "__main__":
    unittest.main()

