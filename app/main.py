from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.summarizer.summarizer import Summarizer
from app.critic.critic import Critic
from app.reducer.reducer import Reducer
from app.finalizer.finalizer import Finalizer
from app.reducer.reducer_model import ReducerInput, CriticFeedback
from app.api.nats_handler import broker, PROGRESS_SUBJECT

app = FastAPI()

summarizer = Summarizer()
critic = Critic()
reducer = Reducer()
finalizer = Finalizer()

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
    final_summaries = []

    for i, chunk in enumerate(data.chunks):
        # берём контекст
        context = data.chunks[max(0, i - CONTEXT_SIZE): i]
        context_text = "\n".join(context)
        full_input = f"Контекст:\n{context_text}\n\nТекущий фрагмент:\n{chunk}" if context else chunk

        # шаг 1: саммари
        summary = await summarizer.run(full_input)

        # шаг 2: критик
        review = await critic.run(summary)

        # шаг 3: если критик не подтвердил → Reducer
        if review.get("score") != "confirmed":
            reducer_input = ReducerInput(
                original=chunk,
                summary=summary,
                feedback=CriticFeedback(**review)
            )
            summary = await reducer.run(reducer_input)

        # публикуем промежуточный результат в NATS
        await broker.publish(
            {"chunk_index": i, "summary": summary},
            subject=PROGRESS_SUBJECT
        )

        final_summaries.append(summary)

    # общий итог
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

    return {"final_summary": final_summary}
