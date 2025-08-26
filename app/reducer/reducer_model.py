from pydantic import BaseModel
from typing import Literal

class CriticFeedback(BaseModel):
    score: Literal["confirmed", "refine", "discard"]
    reason: str

class ReducerInput(BaseModel):
    original: str         # Оригинальный текст диалога
    summary: str          # Саммари до правки
    feedback: CriticFeedback  # Замечания критика