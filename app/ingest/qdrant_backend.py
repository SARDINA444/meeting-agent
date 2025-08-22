from qdrant_client import QdrantClient, models

class QdrantBackend:
    def __init__(self, host="qdrant", port=6333):
        self.client = QdrantClient(host=host, port=port)

    def save_vector(self, collection: str, vector: list[float], payload: dict):
        self.client.upsert(
            collection_name=collection,
            points=[models.PointStruct(
                id=payload.get("id"),
                vector=vector,
                payload=payload
            )]
        )
