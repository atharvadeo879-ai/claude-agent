"""Phase 4: embeddings and vector retrieval abstraction."""

from dataclasses import dataclass


def _simple_embed(text: str) -> list[float]:
    text = text.strip().lower()
    return [float(sum(ord(char) for char in text) % 1000), float(len(text))]


def _distance(vec1: list[float], vec2: list[float]) -> float:
    return abs(vec1[0] - vec2[0]) + abs(vec1[1] - vec2[1])


@dataclass(frozen=True)
class VectorDocument:
    doc_id: str
    text: str
    embedding: list[float]


class InMemoryVectorStore:
    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name
        self._docs: list[VectorDocument] = []

    def upsert(self, doc_id: str, text: str) -> None:
        embedding = _simple_embed(text)
        self._docs = [doc for doc in self._docs if doc.doc_id != doc_id]
        self._docs.append(VectorDocument(doc_id=doc_id, text=text, embedding=embedding))

    def search(self, query: str, top_k: int = 3) -> list[VectorDocument]:
        query_embedding = _simple_embed(query)
        ranked = sorted(self._docs, key=lambda doc: _distance(doc.embedding, query_embedding))
        return ranked[: max(top_k, 0)]


class VectorStoreFactory:
    @staticmethod
    def create(provider: str) -> InMemoryVectorStore:
        normalized = provider.strip().lower()
        if normalized not in {"chromadb", "pinecone"}:
            raise ValueError("provider must be chromadb or pinecone")
        return InMemoryVectorStore(provider_name=normalized)


class EmbeddingService:
    def __init__(self, provider: str) -> None:
        self.store = VectorStoreFactory.create(provider)

    def embed_and_store(self, doc_id: str, text: str) -> None:
        self.store.upsert(doc_id=doc_id, text=text)

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        return [doc.text for doc in self.store.search(query=query, top_k=top_k)]

