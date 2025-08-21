import asyncio
from typing import List


class ASRService:
    """
    Заглушка для ASR (распознавания речи).
    Имитирует нарезку аудио на чанки и их "распознавание".
    """

    def __init__(self, chunk_size: int = 5):
        self.chunk_size = chunk_size

    async def transcribe(self, audio: str) -> List[str]:
        """
        Имитация распознавания речи.
        audio: строка, имитирующая входное аудио (например, "это длинная запись...")
        Возвращает список чанков-транскрибированного текста.
        """
        await asyncio.sleep(0.1)  # имитация задержки
        words = audio.split()
        chunks = [
            " ".join(words[i : i + self.chunk_size])
            for i in range(0, len(words), self.chunk_size)
        ]
        return chunks


# Создаём глобальный объект ASR для использования в main.py
asr_service = ASRService()
