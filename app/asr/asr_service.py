def fake_asr(text: str) -> str:
    return text


def fake_asr_split(text: str, chunk_size: int = 20):
    """
    Имитация ASR: режем текст на чанки фиксированного размера.
    Например, из длинной строки получаем список коротких фрагментов.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
