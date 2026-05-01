"""Local runner for manual UI testing."""

from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from phases.phase7 import GroqClient, Phase7Service


def _load_env_file() -> None:
    env_path = os.path.join(os.path.dirname(__file__), "phases", "phase6", ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key and value and key not in os.environ:
                os.environ[key] = value


class AppHandler(BaseHTTPRequestHandler):
    service = Phase7Service(groq_client=GroqClient(), vector_provider="chromadb", daily_limit=100000)

    def _render(self, prompt: str = "") -> bytes:
        if prompt.strip():
            generation_result = self.service.generate_architecture(
                user_id="manual-user",
                date_key="2026-05-01",
                prompt=prompt,
            )
            history = [f"Prompt: {prompt[:60]}"]
        else:
            generation_result = {
                "sections": {"Overview": "Submit a prompt to generate architecture output."},
                "token_usage": {
                    "current_request_tokens": 0,
                    "used_today": 0,
                    "remaining_today": self.service.token_service.daily_limit,
                    "usage_ratio": 0.0,
                },
            }
            history = []

        page = self.service.build_ui_page(
            generation_result,
            history_items=history,
            prompt_value=prompt,
        )
        return page.encode("utf-8")

    def do_GET(self) -> None:  # noqa: N802
        payload = self._render()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        prompt = parse_qs(body).get("prompt", [""])[0]
        try:
            payload = self._render(prompt)
            status = 200
        except Exception as exc:  # noqa: BLE001
            payload = f"<html><body><h2>Error</h2><pre>{exc}</pre></body></html>".encode("utf-8")
            status = 500
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    _load_env_file()
    host = "127.0.0.1"
    port = 8000
    server = HTTPServer((host, port), AppHandler)
    print(f"Manual test server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

