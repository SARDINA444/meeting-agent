from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.summarizer.summarizer import simple_summarizer, critic
from app.reducer.reducer import Reducer
from .ingest.redis_backend import RedisBackend

app = FastAPI(title="RAG Pipeline")

# Глобальные объекты (можно заменить на зависимости через Depends)
reducer = Reducer()
state_backend = RedisBackend()


class ChunksRequest(BaseModel):
    chunks: List[str]
    session_id: str = "default_session"


@app.post("/process/")
def process_chunks(req: ChunksRequest):
    """
    API: принимает список чанков текста, обрабатывает их пайплайном,
    сохраняет rolling summary + open_items в Redis.
    """
    for chunk in req.chunks:
        # Summarizer
        summary = simple_summarizer([chunk], max_len=100)

        # Critic
        critic_result = critic(summary)

        # Reducer
        rolling_summary = reducer.reduce(summary, critic_result)

        # Persist (Redis)
        state_backend.save_state(req.session_id, reducer.get_state())

    return {
        "session_id": req.session_id,
        "rolling_summary": reducer.rolling_summary,
        "open_items": reducer.open_items,
    }


@app.get("/state/{session_id}")
def get_state(session_id: str):
    """
    API: возвращает сохранённое состояние по session_id
    """
    state = state_backend.load_state(session_id)
    return state or {"error": "no state found"}
