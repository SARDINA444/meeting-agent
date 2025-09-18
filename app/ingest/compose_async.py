from redis import asyncio as aioredis
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct
from typing import List


class ComposeAsync:
    def __init__(self, redis: aioredis.Redis, qdrant: AsyncQdrantClient, collection_name: str = "summaries"):
        self.redis = redis
        self.qdrant = qdrant
        self.collection_name = collection_name

    async def save_intermediate(self, process_id: str, step: int, summary: str):
        key = f"process:{process_id}:step:{step}"
        await self.redis.set(key, summary)

    async def get_intermediate(self, process_id: str, step: int) -> str | None:
        key = f"process:{process_id}:step:{step}"
        return await self.redis.get(key)

    async def list_intermediates(self, process_id: str) -> List[str]:
        keys = await self.redis.keys(f"process:{process_id}:step:*")
        keys = sorted(keys, key=lambda x: int(x.split(":")[-1]))
        return [await self.redis.get(k) for k in keys]

    async def save_final(self, process_id: str, summary: str, vector: List[float]):
        point = PointStruct(
            id=process_id,
            vector=vector,
            payload={"summary": summary},
        )
        await self.qdrant.upsert(collection_name=self.collection_name, points=[point])

    async def get_final(self, process_id: str) -> str | None:
        result = await self.qdrant.retrieve(collection_name=self.collection_name, ids=[process_id])
        if result:
            return result[0].payload.get("summary")
        return None
