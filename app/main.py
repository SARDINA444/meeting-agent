from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from app.pipeline import process_meeting
from app.api.nats_handler import run_nats

app = FastAPI(title="Meeting Agent MVP")


class InputText(BaseModel):
    text: str


@app.post("/api/process")
async def process(input_text: InputText):
    result = process_meeting(input_text.text)
    return result


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(run_nats())
