# app/ingest/compose.py
from app.ingest.redis_backend import RedisBackend
from app.ingest.qdrant_backend import QdrantBackend

class Compose:
    """
    Объединённая обёртка над Redis (промежуточные summary) и Qdrant (финальные summary).
    Предполагаем, что QdrantBackend сам знает свою коллекцию и размерность, либо создаёт по умолчанию.
    """
    def __init__(self, redis_url="redis://redis:6379/0", qdrant_url="http://qdrant:6333"):
        self.redis_backend = RedisBackend(redis_url)

        # Пробуем максимально совместимо и просто
        try:
            # если твой backend принимает только url
            self.qdrant_backend = QdrantBackend(qdrant_url)
        except TypeError:
            # если принимает (url, collection_name)
            self.qdrant_backend = QdrantBackend(qdrant_url, "summaries")

    # --- Redis (intermediate) ---
    def save_intermediate(self, process_id: str, step: int, summary: str):
        self.redis_backend.save_intermediate(process_id, step, summary)

    def get_intermediate(self, process_id: str, step: int):
        return self.redis_backend.get_intermediate(process_id, step)

    def list_intermediates(self, process_id: str):
        return self.redis_backend.list_intermediates(process_id)

    # --- Qdrant (final) ---
    def save_final(self, process_id: str, summary: str, vector: list[float]):
        self.qdrant_backend.save_final(process_id, summary, vector)

    def get_final(self, process_id: str):
        return self.qdrant_backend.get_final(process_id)
