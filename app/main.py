from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.summarizer.summarizer import advanced_summarizer, Critic
from app.reducer.reducer import Reducer
from app.finalizer.finalizer import Finalizer, FinalCritic
from .integrators.calendar_jira_api import CalendarJiraAPI

app = FastAPI(title="AI Processing Pipeline")


# --- Модели запросов/ответов ---
class TextRequest(BaseModel):
    text: str  # текст передаётся напрямую через JSON


class PipelineResponse(BaseModel):
    chunks: List[str]
    summaries: List[str]
    reduced_summary: str
    final_summary: str
    calendar_payload: dict
    jira_payload: dict


@app.post("/process", response_model=PipelineResponse)
async def process_text(req: TextRequest):
    """
    Полный пайплайн без ASR:
    Текст передаётся напрямую через JSON.
    """

    text = req.text

    # Разбиваем текст на чанки по предложениям
    chunks = [c.strip() for c in text.split(".") if c.strip()]

    # Инициализация компонентов
    critic = Critic()
    reducer = Reducer()
    finalizer = Finalizer()
    final_critic = FinalCritic()
    summaries = []

    # Summarizer + Critic + Reducer
    for chunk in chunks:
        summary = advanced_summarizer(chunk)
        critic.validate(summary)
        summaries.append(summary)
        reducer.add_chunk_summary(summary, open_item=f"todo: проверить '{chunk[:20]}'")

    # Reducer: rolling summary
    reducer_state = reducer.get_state()
    reduced_summary = reducer_state["rolling_summary"]

    # Finalizer
    final_data = finalizer.build_final_summary(reducer_state)
    final_summary = final_data["final_summary"]

    # FinalCritic
    final_critic.validate(final_summary, final_data["final_open_items"])

    # Интеграции (моки)
    calendar_payload = CalendarJiraAPI.to_calendar(final_summary, final_data["final_open_items"])
    jira_payload = CalendarJiraAPI.to_jira(final_summary, final_data["final_open_items"])

    return PipelineResponse(
        chunks=chunks,
        summaries=summaries,
        reduced_summary=reduced_summary,
        final_summary=final_summary,
        calendar_payload=calendar_payload,
        jira_payload=jira_payload,
    )
