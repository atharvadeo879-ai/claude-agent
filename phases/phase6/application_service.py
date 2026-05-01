"""Phase 6: integration service over phases 1-5."""

from phases.phase1 import ArchitectureFormatter, PromptRequest, validate_request
from phases.phase2 import TokenUsageService
from phases.phase3 import RevisionManager
from phases.phase4 import EmbeddingService
from phases.phase5 import MetricsCollector, RetryExecutor


class ClaudeAgentService:
    def __init__(self, vector_provider: str = "chromadb", daily_limit: int = 100000) -> None:
        self.formatter = ArchitectureFormatter()
        self.token_service = TokenUsageService(daily_limit=daily_limit)
        self.revision_manager = RevisionManager()
        self.embedding_service = EmbeddingService(provider=vector_provider)
        self.metrics = MetricsCollector()
        self.retry = RetryExecutor(max_attempts=2)

    def generate_architecture(self, user_id: str, date_key: str, prompt: str) -> dict:
        request = PromptRequest(user_id=user_id, prompt=prompt)
        validate_request(request)

        for idx, sentence in enumerate(prompt.split(".")):
            sentence = sentence.strip()
            if sentence:
                self.embedding_service.embed_and_store(doc_id=f"seed-{idx}", text=sentence)

        def _call_llm_stub() -> str:
            context = self.embedding_service.retrieve(prompt, top_k=2)
            return f"Generated architecture using context: {' | '.join(context)}"

        result, latency_ms = self.retry.run(_call_llm_stub)
        self.metrics.record(is_success=True, latency_ms=latency_ms)
        sections = self.formatter.format(result)

        prompt_tokens = len(prompt.split())
        completion_tokens = len(result.split())
        current_tokens = self.token_service.record_usage(user_id, date_key, prompt_tokens, completion_tokens)
        quota = self.token_service.get_daily_quota(user_id, date_key)

        return {
            "sections": sections,
            "token_usage": {
                "current_request_tokens": current_tokens,
                "used_today": quota.used_today,
                "remaining_today": quota.remaining_today,
                "usage_ratio": quota.usage_ratio,
            },
        }

    def edit_prompt(self, response_id: str, edited_prompt: str) -> int:
        rev = self.revision_manager.add_revision(response_id, "prompt_edit", edited_prompt)
        return rev.revision_id

    def edit_response(self, response_id: str, edited_response: str) -> int:
        rev = self.revision_manager.add_revision(response_id, "response_edit", edited_response)
        return rev.revision_id

