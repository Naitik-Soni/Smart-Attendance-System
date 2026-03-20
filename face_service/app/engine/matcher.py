from app.core.config import settings
from app.vector.embedding_store import EmbeddingStore
from app.vector.id_map import IDMapStore


class FaceMatcher:
    def __init__(self, store: EmbeddingStore, id_map: IDMapStore):
        self.store = store
        self.id_map = id_map

    def match(self, embedding, source_type: str, threshold_override: float | None = None) -> dict:
        if self.store.index.ntotal == 0:
            return {"status": "unknown", "confidence": None, "payload": None}

        scores, ids = self.store.search(embedding, top_k=1)
        score = float(scores[0][0])
        idx = int(ids[0][0])
        threshold = float(threshold_override) if threshold_override is not None else float(settings.CONFIDENCE_THRESHOLD)
        # Strict policy rule: match only when confidence > threshold.
        if idx < 0 or score <= threshold:
            return {"status": "unknown", "confidence": score, "payload": None}

        payload = self.id_map.get(idx)
        if payload is None:
            return {"status": "unknown", "confidence": score, "payload": None}

        return {"status": "matched", "confidence": score, "payload": payload}
