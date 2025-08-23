from typing import Union, List

try:
    from transformers import pipeline
    _hf_summarizer = pipeline("summarization")
except Exception:
    _hf_summarizer = None  # fallback, если transformers недоступны


def advanced_summarizer(
    text_or_chunks: Union[str, List[str]],
    max_words: int = 80,
    min_words: int = 10
) -> str:
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


# --- Critic для проверки summary ---
class Critic:
    def validate(self, summary: str):
        """
        Базовая проверка summary.
        """
        if not summary:
            raise ValueError("Summary не может быть пустым")
