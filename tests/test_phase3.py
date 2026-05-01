import unittest

from phases.phase3 import RevisionManager


class TestPhase3(unittest.TestCase):
    def test_adds_prompt_and_response_revisions(self):
        manager = RevisionManager()
        r1 = manager.add_revision("resp-1", "prompt_edit", "edited prompt")
        r2 = manager.add_revision("resp-1", "response_edit", "edited response")
        history = manager.get_history("resp-1")
        self.assertEqual(r1.revision_id, 1)
        self.assertEqual(r2.revision_id, 2)
        self.assertEqual(len(history), 2)


if __name__ == "__main__":
    unittest.main()

