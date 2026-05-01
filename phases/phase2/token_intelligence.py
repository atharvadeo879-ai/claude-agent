"""Phase 2: daily token usage and quota calculations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyQuota:
    used_today: int
    daily_limit: int

    @property
    def remaining_today(self) -> int:
        return max(self.daily_limit - self.used_today, 0)

    @property
    def usage_ratio(self) -> float:
        if self.daily_limit <= 0:
            return 1.0
        return min(self.used_today / self.daily_limit, 1.0)


class TokenUsageService:
    def __init__(self, daily_limit: int = 100000) -> None:
        self.daily_limit = daily_limit
        self._ledger: dict[tuple[str, str], int] = {}

    def record_usage(self, user_id: str, date_key: str, prompt_tokens: int, completion_tokens: int) -> int:
        total = max(prompt_tokens, 0) + max(completion_tokens, 0)
        key = (user_id, date_key)
        self._ledger[key] = self._ledger.get(key, 0) + total
        return total

    def get_daily_quota(self, user_id: str, date_key: str) -> DailyQuota:
        used = self._ledger.get((user_id, date_key), 0)
        return DailyQuota(used_today=used, daily_limit=self.daily_limit)

