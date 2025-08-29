from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.summarizer.summarizer import Summarizer
from app.critic.critic import Critic
from app.reducer.reducer import Reducer
from app.finalizer.finalizer import Finalizer
from app.reducer.reducer_model import ReducerInput, CriticFeedback


app = FastAPI()

summarizer = Summarizer()
critic = Critic()
reducer = Reducer()
finalizer = Finalizer()

# сколько предыдущих чанков брать в контекст
CONTEXT_SIZE = 2


class ChunksRequest(BaseModel):
    chunks: List[str]


@app.post("/process/")
async def process_chunks(data: ChunksRequest):
    final_summaries = []

    for i, chunk in enumerate(data.chunks):
        # берём контекст из предыдущих чанков
        context = data.chunks[max(0, i - CONTEXT_SIZE): i]
        context_text = "\n".join(context)

        # передаём Summarizer текущий чанк + контекст
        full_input = f"Контекст:\n{context_text}\n\nТекущий фрагмент:\n{chunk}" if context else chunk
        summary = await summarizer.run(full_input)

        # проверка критиком
        review = await critic.run(summary)

        # если нужно — исправляем через Reducer
        if review.get("score") != "confirmed":
            reducer_input = ReducerInput(
                original=chunk,
                summary=summary,
                feedback=CriticFeedback(**review)
            )
            summary = await reducer.run(reducer_input)

        # в финальный список идёт summary (подтверждённое или исправленное)
        final_summaries.append(summary)

    # общий итог
    combined_summary = "\n".join(final_summaries)

    # финализация
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

    return {
        "final_summary": final_summary,
    }
