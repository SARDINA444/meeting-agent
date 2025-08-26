from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.summarizer.summarizer import Summarizer
from app.critic.critic import Critic
from app.reducer.reducer import Reducer
from app.reducer.reducer_model import ReducerInput, CriticFeedback


app = FastAPI()

summarizer = Summarizer()
critic = Critic()
reducer = Reducer()


class ChunksRequest(BaseModel):
    chunks: List[str]


@app.post("/process/")
async def process_chunks(data: ChunksRequest):
    final_summaries = []
    critics = []
    reduced = []

    for chunk in data.chunks:
        # Шаг 1. Саммари
        summary = await summarizer.run(chunk)

        # Шаг 2. Проверка критиком
        review = await critic.run(summary)
        critics.append(review)

        # Шаг 3. Если критик не подтвердил → исправляем через Reducer
        if review.get("score") != "confirmed":
            reducer_input = ReducerInput(
                original=chunk,
                summary=summary,
                feedback=CriticFeedback(**review)
            )
            summary = await reducer.run(reducer_input)
            reduced.append(summary)
        else:
            reduced.append(None)

        # В финальный список идёт исправленное (или подтверждённое) summary
        final_summaries.append(summary)

    # Склеиваем в общий итог
    combined_summary = "\n".join(final_summaries)

    return {
        "final_summaries": final_summaries,   # итоговые саммари чанков
        "combined_summary": combined_summary, # общий текст
        "critics": critics,                   # результаты проверки критика
        "reduced": reduced                    # какие саммари были исправлены
    }
