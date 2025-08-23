from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ReducerState:
    """
    Состояние редьюсера: rolling_summary и список открытых пунктов.
    """
    rolling_summary: str = ""
    open_items: List[str] = field(default_factory=list)


class Reducer:
    def __init__(self):
        # У каждого экземпляра свой state
        self.state = ReducerState()

    def add_chunk_summary(self, chunk_summary: str, open_item: str = None) -> None:
        """
        Добавляем новый summary чанка и (опционально) открытый пункт.
        """
        if self.state.rolling_summary:
            self.state.rolling_summary += " " + chunk_summary
        else:
            self.state.rolling_summary = chunk_summary

        if open_item:
            self.state.open_items.append(open_item)

    def get_state(self) -> Dict[str, Any]:
        """
        Получаем текущее состояние в виде словаря (для сохранения в Redis/Qdrant).
        """
        return {
            "rolling_summary": self.state.rolling_summary,
            "open_items": self.state.open_items,
        }

    def load_state(self, data: Dict[str, Any]) -> None:
        """
        Восстанавливаем состояние из словаря.
        """
        self.state.rolling_summary = data.get("rolling_summary", "")
        self.state.open_items = data.get("open_items", [])

    def reset(self) -> None:
        """
        Сбрасываем состояние.
        """
        self.state = ReducerState()
