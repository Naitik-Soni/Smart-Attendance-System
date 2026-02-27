from app.core.config import settings
from app.vector.embedding_store import EmbeddingStore
from app.vector.id_map import IDMapStore


class FaceMatcher:
    def __init__(self, store: EmbeddingStore, id_map: IDMapStore):
        self.store = store
        self.id_map = id_map

    def _threshold_for_source(self, source_type: str) -> float:
        source = source_type.lower()
        if source == "ceiling_camera":
            return max(0.65, settings.CONFIDENCE_THRESHOLD - 0.05)
        if source == "upload_image":
            return max(0.70, settings.CONFIDENCE_THRESHOLD)
        return max(0.75, settings.CONFIDENCE_THRESHOLD)

    def match(self, embedding, source_type: str) -> dict:
        if self.store.index.ntotal == 0:
            return {"status": "unknown", "confidence": None, "payload": None}

        scores, ids = self.store.search(embedding, top_k=1)
        score = float(scores[0][0])
        idx = int(ids[0][0])
        threshold = self._threshold_for_source(source_type)
        if idx < 0 or score < threshold:
            return {"status": "unknown", "confidence": score, "payload": None}

        payload = self.id_map.get(idx)
        if payload is None:
            return {"status": "unknown", "confidence": score, "payload": None}

        return {"status": "matched", "confidence": score, "payload": payload}
