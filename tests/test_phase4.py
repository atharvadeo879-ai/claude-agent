import unittest

from phases.phase4 import EmbeddingService


class TestPhase4(unittest.TestCase):
    def test_retrieves_from_chromadb_provider(self):
        svc = EmbeddingService(provider="chromadb")
        svc.embed_and_store("1", "token usage details")
        svc.embed_and_store("2", "architecture sections")
        matches = svc.retrieve("architecture", top_k=1)
        self.assertEqual(len(matches), 1)

    def test_retrieves_from_pinecone_provider(self):
        svc = EmbeddingService(provider="pinecone")
        svc.embed_and_store("1", "groq llm integration")
        matches = svc.retrieve("llm", top_k=1)
        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()

