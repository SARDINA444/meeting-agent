from fastapi import FastAPI
from app.asr.asr_service import asr_service
from app.summarizer.summarizer import simple_summarizer, critic

app = FastAPI(title="Meeting Agent")


@app.get("/")
async def root():
    return {"message": "Meeting Agent API is running"}


@app.post("/asr/")
async def asr_endpoint(audio: str):
    """
    Эндпоинт: имитация распознавания аудио → чанки текста.
    """
    chunks = await asr_service.transcribe(audio)
    return {"chunks": chunks}


@app.post("/process/")
async def process_endpoint(audio: str):
    """
    Эндпоинт: полный пайплайн (ASR → Summarizer → Critic).
    """
    chunks = await asr_service.transcribe(audio)
    summary = simple_summarizer(chunks)
    critic_result = critic(summary)
    return {
        "chunks": chunks,
        "summary": summary,
        "critic": critic_result,
    }
