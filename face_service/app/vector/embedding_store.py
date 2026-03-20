from pathlib import Path

import numpy as np

try:
    import faiss
except Exception:  # pragma: no cover
    faiss = None


class _MemoryIndex:
    def __init__(self, dim: int):
        self.dim = dim
        self.vectors = np.zeros((0, dim), dtype=np.float32)

    @property
    def ntotal(self) -> int:
        return self.vectors.shape[0]

    def add(self, embeddings: np.ndarray) -> None:
        if embeddings.size == 0:
            return
        self.vectors = np.vstack([self.vectors, embeddings])

    def search(self, query: np.ndarray, top_k: int):
        if self.ntotal == 0:
            return np.zeros((1, top_k), dtype=np.float32), -np.ones((1, top_k), dtype=np.int64)
        sims = np.dot(self.vectors, query[0])
        order = np.argsort(-sims)[:top_k]
        scores = sims[order]
        return scores.reshape(1, -1).astype(np.float32), order.reshape(1, -1).astype(np.int64)

    def reconstruct(self, i: int) -> np.ndarray:
        return self.vectors[i]


class EmbeddingStore:
    def __init__(self, dim: int, index_path: str):
        self.dim = dim
        self.index_path = Path(index_path)
        self.index = self._new_index()

    def _new_index(self):
        if faiss is None:
            return _MemoryIndex(self.dim)
        return faiss.IndexFlatIP(self.dim)

    def load(self) -> None:
        if faiss is not None and self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = self._new_index()

    def save(self) -> None:
        if faiss is None:
            return
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))

    def add(self, embeddings: np.ndarray) -> list[int]:
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
        start = self.index.ntotal
        self.index.add(embeddings)
        end = self.index.ntotal
        return list(range(start, end))

    def search(self, embedding: np.ndarray, top_k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        if embedding.dtype != np.float32:
            embedding = embedding.astype(np.float32)
        scores, ids = self.index.search(embedding, top_k)
        return scores, ids

    def rebuild_without(self, remove_ids: list[int]) -> None:
        if not remove_ids:
            return

        total = self.index.ntotal
        keep = [i for i in range(total) if i not in set(remove_ids)]
        if not keep:
            self.index = self._new_index()
            return

        vectors = np.vstack([self.index.reconstruct(i) for i in keep]).astype(np.float32)
        self.index = self._new_index()
        self.index.add(vectors)
