from app.core.config import settings
from app.engine.matcher import FaceMatcher
from app.vector.embedding_store import EmbeddingStore
from app.vector.id_map import IDMapStore


embedding_store = EmbeddingStore(settings.EMBEDDING_DIM, settings.FAISS_INDEX_PATH)
id_map_store = IDMapStore(settings.FAISS_ID_MAP_PATH)
matcher = FaceMatcher(embedding_store, id_map_store)


def initialize_vector_state() -> None:
    embedding_store.load()
    id_map_store.load()
