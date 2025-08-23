"""
Summarizer — модуль для создания краткого изложения текста.
На текущем этапе используем простую эвристику: берём первые N предложений.
Позже можно заменить на TextRank, HuggingFace или внешний API.
"""

import re
from typing import List


def simple_summarizer(text: str, max_sentences: int = 2) -> str:
    """
    Простейший summarizer: берёт первые N предложений из текста.

    :param text: исходный текст
    :param max_sentences: сколько предложений оставить
    :return: summary (краткое изложение)
    """
    # Разбиваем текст на предложения
    sentences = re.split(r"[.!?]", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    summary_sentences = sentences[:max_sentences]
    return ". ".join(summary_sentences) + ("." if summary_sentences else "")


class Critic:
    """
    Мок-критик: проверяет простейшие свойства summary.
    Позже можно усложнить (например, проверка фактов, длины, релевантности).
    """

    def __init__(self, max_length: int = 200):
        self.max_length = max_length

    def validate(self, summary: str) -> List[str]:
        """
        Проверка summary на валидность.
        :param summary: итоговое summary
        :return: список предупреждений
        """
        issues = []

        if not summary:
            issues.append("Summary is empty.")

        if len(summary) > self.max_length:
            issues.append("Summary is too long.")

        if len(summary.split()) < 3:
            issues.append("Summary seems too short.")

        return issues
