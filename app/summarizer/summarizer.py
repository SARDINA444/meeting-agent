def fake_summarizer(text: str) -> str:
    '''
    Заглушка
    '''
    return text.upper()


def simple_summarizer(chunks, max_len: int = 100):
    """
    Stub summarizer:
    - соединяет чанки
    - обрезает результат до max_len символов
    """
    text = " ".join(chunks)
    return text[:max_len]
