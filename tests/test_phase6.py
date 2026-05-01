import unittest

from phases.phase6 import ClaudeAgentService


class TestPhase6(unittest.TestCase):
    def test_generation_flow_and_usage(self):
        service = ClaudeAgentService(vector_provider="chromadb", daily_limit=1000)
        result = service.generate_architecture(
            user_id="u-1",
            date_key="2026-05-01",
            prompt="Build an architecture summary with data flow and risks.",
        )
        self.assertIn("sections", result)
        self.assertIn("token_usage", result)
        self.assertIn("Overview", result["sections"])
        self.assertGreater(result["token_usage"]["used_today"], 0)

    def test_edit_apis_create_revisions(self):
        service = ClaudeAgentService()
        prompt_rev = service.edit_prompt("resp-1", "new prompt")
        response_rev = service.edit_response("resp-1", "new response")
        self.assertEqual(prompt_rev, 1)
        self.assertEqual(response_rev, 2)


if __name__ == "__main__":
    unittest.main()

