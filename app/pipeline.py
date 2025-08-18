from app.asr.asr_service import fake_asr
from app.summarizer.summarizer import fake_summarizer


def process_meeting(input_text: str) -> dict:
    transcription = fake_asr(input_text)
    summary = fake_summarizer(transcription)
    return {"summary": summary}
