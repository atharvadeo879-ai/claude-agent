"""Phase 7: Groq LLM integration client."""

from __future__ import annotations

import json
import os
from typing import Callable
from urllib import request


class GroqClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "llama-3.3-70b-versatile",
        transport: Callable[[request.Request], str] | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.transport = transport or self._default_transport

    def validate_api_key(self) -> None:
        if not self.api_key.strip():
            raise ValueError("GROQ_API_KEY is required")

    def generate(self, prompt: str) -> str:
        self.validate_api_key()
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        req = request.Request(
            url="https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        raw = self.transport(req)
        parsed = json.loads(raw)
        return parsed["choices"][0]["message"]["content"].strip()

    @staticmethod
    def _default_transport(req: request.Request) -> str:
        with request.urlopen(req, timeout=20) as response:  # noqa: S310
            return response.read().decode("utf-8")

