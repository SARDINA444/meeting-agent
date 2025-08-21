# app/summarizer/summarizer.py
from __future__ import annotations
from typing import List, Union

# Опционально: продвинутый summarizer через transformers.
# Если библиотек нет — всё работает через simple_summarizer.
try:
    from transformers import pipeline  # type: ignore
    _hf_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception:
    _hf_summarizer = None


def simple_summarizer(chunks: List[str], max_len: int = 200) -> str:
    """
    Простой summarizer для Дня 2–3:
    - соединяет чанки в текст
    - обрезает до max_len символов
    """
    text = " ".join(chunks).strip()
    return text[:max_len]


def advanced_summarizer(text_or_chunks: Union[str, List[str]],
                        max_words: int = 80,
                        min_words: int = 10) -> str:
    """
    Продвинутый summarizer:
    - принимает строку ИЛИ список чанков
    - если transformers доступны — использует модель
    - иначе делает простое усечение по словам (fallback)
    """
    if isinstance(text_or_chunks, list):
        full_text = " ".join(text_or_chunks).strip()
    else:
        full_text = text_or_chunks.strip()

    if not full_text:
        return ""

    if _hf_summarizer:
        # В max_length/min_length передаём приблизительные числа слов * 1.5 (эвристика)
        max_len_tokens = int(max_words * 1.5)
        min_len_tokens = max(5, int(min_words * 1.5))
        result = _hf_summarizer(
            full_text,
            max_length=max_len_tokens,
            min_length=min_len_tokens,
            do_sample=False,
            truncation=True,
        )
        return result[0]["summary_text"].strip()

    # Fallback: усечение по словам
    words = full_text.split()
    return " ".join(words[:max_words]).strip()


def critic(summary: str) -> dict:
    """
    Базовая проверка качества summary:
    - непустое
    - не слишком короткое
    - не слишком длинное
    """
    issues = []

    word_count = len(summary.split())
    if not summary.strip():
        issues.append("Summary is empty.")
    if word_count < 5:
        issues.append("Summary is too short.")
    if word_count > 60:
        issues.append("Summary is too long.")

    return {
        "summary": summary,
        "valid": len(issues) == 0,
        "issues": issues,
    }
