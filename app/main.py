from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.summarizer.summarizer import Summarizer
from app.critic.critic import Critic


app = FastAPI()

summarizer = Summarizer()
critic = Critic()


class ChunksRequest(BaseModel):
    chunks: List[str]


@app.post("/process/")
async def process_chunks(data: ChunksRequest):
    # Шаг 1. Прогоняем каждый чанк через Summarizer
    summaries = []
    for chunk in data.chunks:
        summary = await summarizer.run(chunk)
        summaries.append(summary)

    # Шаг 2. Склеиваем все частичные саммари
    combined_summary = "\n".join(summaries)

    # Шаг 3. Проверяем через Critic
    review = await critic.run(combined_summary)

    return {
        "summaries": summaries,
        "combined_summary": combined_summary,
        "critic": review
    }
