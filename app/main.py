from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import uuid

from redis import asyncio as aioredis
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance

from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings

from app.summarizer.summarizer import Summarizer
from app.critic.critic import Critic
from app.reducer.reducer import Reducer
from app.finalizer.finalizer import Finalizer
from app.reducer.reducer_model import ReducerInput, CriticFeedback
from app.api.nats_handler import broker, PROGRESS_SUBJECT
from app.ingest.compose_async import ComposeAsync


app = FastAPI()

# Константы
GIGA_KEY = os.getenv("GIGA_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "summaries"
VECTOR_SIZE = 1024
CONTEXT_SIZE = 2

# Глобальные клиенты
redis_client: aioredis.Redis = None
qdrant_client: AsyncQdrantClient = None
compose: ComposeAsync = None


class ChunksRequest(BaseModel):
    chunks: List[str]


@app.on_event("startup")
async def startup_event():
    global redis_client, qdrant_client, compose

    # Redis
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    await redis_client.ping()

    # Qdrant
    qdrant_client = AsyncQdrantClient(url=QDRANT_URL)

    collections = await qdrant_client.get_collections()
    if COLLECTION_NAME not in [c.name for c in collections.collections]:
        await qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

    # Compose
    compose = ComposeAsync(redis_client, qdrant_client, COLLECTION_NAME)

    # NATS
    await broker.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await broker.close()
    await redis_client.close()
    await qdrant_client.close()


@app.post("/process/")
async def process_chunks(data: ChunksRequest):
    process_id = str(uuid.uuid4())
    final_summaries = []

    summarizer = Summarizer()
    critic = Critic()
    reducer = Reducer()
    finalizer = Finalizer()

    embeddings = GigaChatEmbeddings(credentials=GIGA_KEY, verify_ssl_certs=False, scope="GIGACHAT_API_B2B")

    for i, chunk in enumerate(data.chunks):
        # контекст
        context = data.chunks[max(0, i - CONTEXT_SIZE): i]
        context_text = "\n".join(context)
        full_input = f"Контекст:\n{context_text}\n\nТекущий фрагмент:\n{chunk}" if context else chunk

        # summarizer
        summary = await summarizer.run(full_input)

        # critic
        review = await critic.run(summary)

        # reducer при необходимости
        if review.get("score") != "confirmed":
            reducer_input = ReducerInput(
                original=chunk,
                summary=summary,
                feedback=CriticFeedback(**review),
            )
            summary = await reducer.run(reducer_input)

        # сохраняем промежуточное в Redis
        await compose.save_intermediate(process_id, i, summary)

        # паблишим прогресс в NATS
        await broker.publish(
            {"process_id": process_id, "chunk_index": i, "summary": summary},
            subject=PROGRESS_SUBJECT,
        )

        final_summaries.append(summary)

    # финализация
    combined_summary = "\n".join(final_summaries)
    final_summary = await finalizer.run(combined_summary)

    # финальная проверка
    final_review = await critic.run(final_summary)
    if final_review.get("score") != "confirmed":
        reducer_input = ReducerInput(
            original=combined_summary,
            summary=final_summary,
            feedback=CriticFeedback(**final_review),
        )
        final_summary = await reducer.run(reducer_input)

    # эмбеддинг финального summary
    vector = await embeddings.aembed_query(final_summary)

    # сохраняем финальный результат в Qdrant
    await compose.save_final(process_id, final_summary, vector)

    return {"process_id": process_id, "final_summary": final_summary}
