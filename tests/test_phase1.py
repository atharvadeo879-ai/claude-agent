import unittest

from phases.phase1 import ArchitectureFormatter, PromptRequest, validate_request


class TestPhase1(unittest.TestCase):
    def test_validate_request_rejects_short_prompt(self):
        with self.assertRaises(ValueError):
            validate_request(PromptRequest(user_id="u1", prompt="short"))

    def test_architecture_formatter_produces_sections(self):
        formatter = ArchitectureFormatter()
        sections = formatter.format("System output")
        self.assertIn("Overview", sections)
        self.assertIn("Next Steps", sections)


if __name__ == "__main__":
    unittest.main()

