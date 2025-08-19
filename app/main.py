import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

from app.pipeline import MeetingPipeline
from app.api.nats_handler import run_nats

app = FastAPI(title="Meeting Agent")

pipeline = MeetingPipeline()

class AudioInput(BaseModel):
    text: str


@app.post("/process/")
async def process_audio(input_data: AudioInput):
    chunks = pipeline.process_audio(input_data.text)
    return {"chunks": chunks}


@app.get("/summary/")
async def get_summary():
    summary = pipeline.summarize()
    return {"summary": summary}


# --- запуск NATS вместе с приложением ---
@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(run_nats(pipeline))  # передаём pipeline в NATS-хэндлер
