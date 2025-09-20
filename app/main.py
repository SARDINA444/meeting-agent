import asyncio
import uuid
import json

from app.api.broker import app, broker
from app.api.config import settings

from redis import asyncio as aioredis
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance

from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings
from app.summarizer.summarizer import Summarizer
from app.critic.critic import Critic
from app.reducer.reducer import Reducer
from app.finalizer.finalizer import Finalizer
from app.reducer.reducer_model import ReducerInput, CriticFeedback
from app.ingest.compose_async import ComposeAsync


# глобальные клиенты
redis_client: aioredis.Redis = None
qdrant_client: AsyncQdrantClient = None
compose: ComposeAsync = None
embeddings: GigaChatEmbeddings = None


@app.on_startup
async def startup():
    global redis_client, qdrant_client, compose, embeddings

    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    await redis_client.ping()

    qdrant_client = AsyncQdrantClient(url=settings.qdrant_url)
    collections = await qdrant_client.get_collections()
    if "summaries" not in [c.name for c in collections.collections]:
        await qdrant_client.create_collection(
            collection_name="summaries",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

    compose = ComposeAsync(redis_client, qdrant_client, "summaries")
    embeddings = GigaChatEmbeddings(
        credentials=settings.giga_key,
        verify_ssl_certs=False,
        scope="GIGACHAT_API_B2B"
    )


@app.on_shutdown
async def shutdown():
    await redis_client.close()
    await qdrant_client.close()


@broker.subscriber(settings.nats_subject_in)
async def handle_message(msg: dict):
    """
    msg = {
        "file_id": "uuid",
        "chunk_index": 3,
        "total_chunks": 10,
        "text": "текст чанка"
    }
    """
    file_id = msg["file_id"]
    chunk_index = msg["chunk_index"]
    total_chunks = msg.get("total_chunks")
    text = msg["text"]

    redis_key = f"summaries:{file_id}"

    summarizer = Summarizer()
    critic = Critic()
    reducer = Reducer()
    finalizer = Finalizer()

    # контекст: берём 2 предыдущих саммари из Redis
    prev_summaries = await redis_client.lrange(redis_key, max(0, chunk_index - 2), chunk_index - 1)
    context_text = "\n".join(prev_summaries) if prev_summaries else ""
    full_input = f"Контекст:\n{context_text}\n\nТекущий фрагмент:\n{text}" if context_text else text

    # summarizer
    summary = await summarizer.run(full_input)

    # critic
    review = await critic.run(summary)
    if review.get("score") != "confirmed":
        reducer_input = ReducerInput(
            original=text,
            summary=summary,
            feedback=CriticFeedback(**review),
        )
        summary = await reducer.run(reducer_input)

    # сохраняем промежуточное саммари
    await redis_client.rpush(redis_key, summary)

    # публикуем промежуточное саммари
    await broker.publish(
        {"file_id": file_id, "chunk_index": chunk_index, "summary": summary},
        subject=settings.nats_subject_intermediate,
    )

    # если это последний чанк — собираем финальное саммари
    if total_chunks is not None and chunk_index + 1 == total_chunks:
        summaries = await redis_client.lrange(redis_key, 0, -1)
        combined_summary = "\n".join(summaries)

        final_summary = await finalizer.run(combined_summary)
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
        await compose.save_final(file_id, final_summary, vector)

        # публикуем финальное саммари
        await broker.publish(
            {"file_id": file_id, "final_summary": final_summary},
            subject=settings.nats_subject_final,
        )

        # очищаем Redis для этого файла
        await redis_client.delete(redis_key)
