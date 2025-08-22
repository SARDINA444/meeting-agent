import pytest
from app.summarizer.summarizer import simple_summarizer, advanced_summarizer, critic


def test_simple_summarizer_and_critic_valid():
    chunks = ["Привет мир", "Это тестовый текст", "Финальная часть"]
    summary = simple_summarizer(chunks, max_len=200)

    # summary должно содержать хотя бы часть текста
    assert "Привет мир" in summary
    assert len(summary) > 0

    # проверяем через critic
    result = critic(summary)
    assert result["valid"] is True
    assert result["issues"] == []


def test_simple_summarizer_truncate():
    chunks = ["слово"] * 100  # длинный список слов
    summary = simple_summarizer(chunks, max_len=20)

    # должно быть обрезано
    assert len(summary) <= 20


def test_critic_empty_summary():
    result = critic("")
    assert result["valid"] is False
    assert "empty" in result["issues"][0].lower()


def test_critic_too_short():
    result = critic("Привет")
    assert result["valid"] is False
    assert "too short" in result["issues"][0].lower()


def test_critic_too_long():
    long_text = " ".join(["слово"] * 100)
    result = critic(long_text)
    assert result["valid"] is False
    assert any("too long" in issue.lower() for issue in result["issues"])


@pytest.mark.skipif(advanced_summarizer.__doc__ is None, reason="advanced_summarizer not available")
def test_advanced_summarizer_fallback_or_model():
    text = "Это длинный текст, который нужно сократить до чего-то более читаемого."
    summary = advanced_summarizer(text, max_words=10)
    assert isinstance(summary, str)
    assert len(summary.split()) <= 10
