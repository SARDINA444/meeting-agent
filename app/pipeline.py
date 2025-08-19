from app.asr.asr_service import fake_asr_split
from app.summarizer.summarizer import simple_summarizer


class MeetingPipeline:
    def __init__(self):
        self.chunks = []

    def process_audio(self, text: str):
        """
        Имитация загрузки аудио и нарезки на чанки через fake_asr_split
        """
        new_chunks = fake_asr_split(text)
        self.chunks.extend(new_chunks)
        return new_chunks

    def summarize(self):
        """Возвращает короткий summary по накопленным чанкам"""
        return simple_summarizer(self.chunks)
