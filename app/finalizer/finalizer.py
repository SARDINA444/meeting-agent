from typing import Dict, List


class Finalizer:
    """
    Объединяет все промежуточные состояния (summary, open_items)
    в финальный отчет.
    """

    def __init__(self):
        self.final_summary: str = ""
        self.final_open_items: List[str] = []

    def build_final_summary(self, reducer_state: Dict) -> Dict:
        """
        Формирует финальный отчет на основе состояния Reducer.
        """
        self.final_summary = reducer_state.get("rolling_summary", "")
        self.final_open_items = reducer_state.get("open_items", [])

        return {
            "final_summary": self.final_summary,
            "final_open_items": self.final_open_items,
        }


class FinalCritic:
    """
    Базовая финальная валидация результата.
    Проверяем, что summary не пустое, а список задач имеет адекватный вид.
    """

    def validate(self, final_summary: str, final_open_items: List[str]) -> Dict:
        errors = []

        if not final_summary or len(final_summary.strip()) < 10:
            errors.append("Final summary слишком короткий или пустой")

        if any(len(item.strip()) == 0 for item in final_open_items):
            errors.append("Есть пустые open items")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
        }


class Integrators:
    """
    Моки интеграций — формируем JSON-структуры для сторонних систем.
    Например, Calendar и Jira.
    """

    @staticmethod
    def to_calendar(final_summary: str, open_items: List[str]) -> Dict:
        return {
            "calendar_event": {
                "title": "Project Meeting",
                "description": final_summary,
                "tasks": open_items,
            }
        }

    @staticmethod
    def to_jira(final_summary: str, open_items: List[str]) -> Dict:
        return {
            "jira_ticket": {
                "summary": final_summary,
                "open_items": open_items,
                "priority": "Medium",
            }
        }
