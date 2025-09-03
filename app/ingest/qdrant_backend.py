from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance


class QdrantBackend:
    def __init__(self, qdrant_url="http://localhost:6333", collection_name="summaries", vector_size=1024):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name

        # создаём коллекцию, если её нет
        if self.collection_name not in [c.name for c in self.qdrant.get_collections().collections]:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )

    def save_final(self, process_id: str, summary: str, vector: list[float]):
        point = PointStruct(
            id=process_id,
            vector=vector,
            payload={"summary": summary}
        )
        self.qdrant.upsert(collection_name=self.collection_name, points=[point])

    def get_final(self, process_id: str) -> str | None:
        result = self.qdrant.retrieve(collection_name=self.collection_name, ids=[process_id])
        if result:
            return result[0].payload["summary"]
        return None
