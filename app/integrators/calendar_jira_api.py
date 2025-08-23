from typing import Dict, List


class CalendarJiraAPI:
    """
    Моки интеграций — формируем JSON-структуры для Calendar и Jira.
    """

    @staticmethod
    def to_calendar(final_summary: str, open_items: List[str]) -> Dict:
        """
        Формирование структуры для календарного события.
        """
        return {
            "calendar_event": {
                "title": "Project Meeting",
                "description": final_summary,
                "tasks": open_items,
            }
        }

    @staticmethod
    def to_jira(final_summary: str, open_items: List[str]) -> Dict:
        """
        Формирование структуры для Jira тикета.
        """
        return {
            "jira_ticket": {
                "summary": final_summary,
                "open_items": open_items,
                "priority": "Medium",
            }
        }
