"""Phase 7 service using Groq generation and UI output."""

from __future__ import annotations

from phases.phase6 import ClaudeAgentService
from phases.phase7.groq_client import GroqClient
from phases.phase7.ui_page import render_architecture_page


class Phase7Service(ClaudeAgentService):
    def __init__(
        self,
        groq_client: GroqClient | None = None,
        vector_provider: str = "chromadb",
        daily_limit: int = 100000,
    ) -> None:
        super().__init__(vector_provider=vector_provider, daily_limit=daily_limit)
        self.groq_client = groq_client or GroqClient()

    def generate_architecture(self, user_id: str, date_key: str, prompt: str) -> dict:
        result = super().generate_architecture(user_id=user_id, date_key=date_key, prompt=prompt)
        groq_text = self.groq_client.generate(
            "Return an architecture-style summary for this request: " + prompt
        )
        result["sections"]["Overview"] = f"Overview: {groq_text}"
        return result

    def build_ui_page(self, generation_result: dict, history_items: list[str], prompt_value: str = "") -> str:
        token_usage = generation_result["token_usage"]
        return render_architecture_page(
            sections=generation_result["sections"],
            token_usage=token_usage,
            daily_limit=self.token_service.daily_limit,
            history_items=history_items,
            prompt_value=prompt_value,
        )

