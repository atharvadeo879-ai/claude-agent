import json
import unittest
from urllib import request

from phases.phase7 import GroqClient, Phase7Service, render_architecture_page


def fake_transport(_: request.Request) -> str:
    return json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": "System architecture generated via Groq."
                    }
                }
            ]
        }
    )


class TestPhase7(unittest.TestCase):
    def test_groq_requires_api_key(self):
        client = GroqClient(api_key="")
        with self.assertRaises(ValueError):
            client.validate_api_key()

    def test_groq_generate_with_test_key_and_fake_transport(self):
        client = GroqClient(api_key="gsk_test_phase7_key", transport=fake_transport)
        output = client.generate("Create architecture")
        self.assertIn("Groq", output)

    def test_ui_renderer_contains_required_elements(self):
        html = render_architecture_page(
            sections={"Overview": "Overview body"},
            token_usage={
                "current_request_tokens": 120,
                "used_today": 500,
                "remaining_today": 9500,
                "usage_ratio": 0.05,
            },
            daily_limit=10000,
            history_items=["Run 1"],
        )
        self.assertIn('id="daily-usage"', html)
        self.assertIn("Daily Tokens Remaining", html)
        self.assertIn('id="edit-prompt"', html)
        self.assertIn('id="edit-response"', html)

    def test_phase7_service_generation_and_ui(self):
        service = Phase7Service(
            groq_client=GroqClient(api_key="gsk_test_phase7_key", transport=fake_transport),
            vector_provider="chromadb",
            daily_limit=10000,
        )
        result = service.generate_architecture(
            user_id="u-7",
            date_key="2026-05-01",
            prompt="Design architecture with usage bar and edit features.",
        )
        self.assertIn("Overview", result["sections"])
        html = service.build_ui_page(result, ["Initial run"])
        self.assertIn("Architecture Session", html)
        self.assertIn("Session History", html)


if __name__ == "__main__":
    unittest.main()

