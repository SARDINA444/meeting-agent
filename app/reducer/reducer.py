from typing import List, Dict

class Reducer:
    def __init__(self):
        self.rolling_summary: str = ""
        self.open_items: List[str] = []

    def reduce(self, summary: str, critic_result: Dict) -> str:
        """
        Обновляет rolling_summary и open_items
        """
        # аккумулируем summary
        if self.rolling_summary:
            self.rolling_summary += " " + summary
        else:
            self.rolling_summary = summary

        # если critic вернул замечания — сохраняем как open_items
        if not critic_result.get("valid", True):
            self.open_items.extend(critic_result.get("issues", []))

        return self.rolling_summary

    def get_state(self) -> Dict:
        return {
            "rolling_summary": self.rolling_summary,
            "open_items": self.open_items,
        }
