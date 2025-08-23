from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.asr.asr_service import transcribe_audio
from app.summarizer.summarizer import simple_summarizer, Critic
from app.reducer.reducer import Reducer
from app.finalizer.finalizer import Finalizer, FinalCritic
from .integrators.calendar_jira_api import CalendarJiraAPI

app = FastAPI(title="AI Processing Pipeline")

# --- Модели запросов/ответов ---
class AudioRequest(BaseModel):
    audio_path: str


class PipelineResponse(BaseModel):
    transcription: str
    chunks: List[str]
    summaries: List[str]
    reduced_summary: str
    final_summary: str
    calendar_payload: dict
    jira_payload: dict


@app.post("/process", response_model=PipelineResponse)
async def process_audio(req: AudioRequest):
    """
    Полный пайплайн: ASR -> Summarizer -> Critic -> Reducer -> Finalizer -> Integrators
    """

    # 1. ASR
    transcription = transcribe_audio(req.audio_path)

    # Разбиваем текст на чанки (по предложениям)
    chunks = [c.strip() for c in transcription.split(".") if c.strip()]
    summaries = []

    # 2. Инициализация компонентов
    critic = Critic()
    reducer = Reducer()
    finalizer = Finalizer()
    final_critic = FinalCritic()

    # 3. Summarizer + Critic + Reducer
    for chunk in chunks:
        summary = simple_summarizer(chunk)
        critic.validate(summary)  # базовая проверка
        summaries.append(summary)
        reducer.add_chunk_summary(summary, open_item=f"todo: проверить '{chunk[:20]}'")

    # 4. Reducer: rolling summary
    reducer_state = reducer.get_state()
    reduced_summary = reducer_state["rolling_summary"]

    # 5. Finalizer
    final_data = finalizer.build_final_summary(reducer_state)
    final_summary = final_data["final_summary"]

    # 6. FinalCritic
    final_critic.validate(final_summary, final_data["final_open_items"])

    # 7. Интеграции (моки)
    calendar_payload = CalendarJiraAPI.to_calendar(final_summary, final_data["final_open_items"])
    jira_payload = CalendarJiraAPI.to_jira(final_summary, final_data["final_open_items"])

    # 8. Возврат
    return PipelineResponse(
        transcription=transcription,
        chunks=chunks,
        summaries=summaries,
        reduced_summary=reduced_summary,
        final_summary=final_summary,
        calendar_payload=calendar_payload,
        jira_payload=jira_payload,
    )
