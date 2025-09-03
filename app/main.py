from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import uuid

from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings

from app.summarizer.summarizer import Summarizer
from app.critic.critic import Critic
from app.reducer.reducer import Reducer
from app.finalizer.finalizer import Finalizer
from app.reducer.reducer_model import ReducerInput, CriticFeedback
from app.api.nats_handler import broker, PROGRESS_SUBJECT
from app.ingest.compose import Compose

app = FastAPI()

summarizer = Summarizer()
critic = Critic()
reducer = Reducer()
finalizer = Finalizer()
compose = Compose()

# GigaChat Embeddings
GIGA_KEY = os.getenv("GIGA_KEY")
embeddings = GigaChatEmbeddings(credentials=GIGA_KEY, verify_ssl_certs=False)

CONTEXT_SIZE = 2


class ChunksRequest(BaseModel):
    chunks: List[str]


@app.on_event("startup")
async def startup_event():
    await broker.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await broker.close()


@app.post("/process/")
async def process_chunks(data: ChunksRequest):
    process_id = str(uuid.uuid4())
    final_summaries = []

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
                feedback=CriticFeedback(**review)
            )
            summary = await reducer.run(reducer_input)

        # сохраняем промежуточное в Redis
        compose.save_intermediate(process_id, i, summary)

        # паблишим прогресс в NATS
        await broker.publish(
            {"process_id": process_id, "chunk_index": i, "summary": summary},
            subject=PROGRESS_SUBJECT
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
            feedback=CriticFeedback(**final_review)
        )
        final_summary = await reducer.run(reducer_input)

    # эмбеддинг финального summary через GigaChat
    vector = embeddings.embed_query(final_summary)
    compose.save_final(process_id, final_summary, vector)

    return {"process_id": process_id, "final_summary": final_summary}
