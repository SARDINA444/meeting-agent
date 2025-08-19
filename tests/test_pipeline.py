from app.pipeline import MeetingPipeline

def test_pipeline_with_fake_asr():
    pipeline = MeetingPipeline()
    text = "Это длинный текст, который мы имитируем как аудио для нарезки на чанки."
    chunks = pipeline.process_audio(text)

    assert len(chunks) > 1, "Должно получиться несколько чанков"
    summary = pipeline.summarize()
    assert isinstance(summary, str)
    assert len(summary) > 0
