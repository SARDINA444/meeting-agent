import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_process_pipeline_advanced_summarizer():
    """
    Проверяем полный пайплайн без ASR с advanced_summarizer:
    - текст передаётся напрямую через JSON
    - Summarizer -> Critic -> Reducer -> Finalizer -> Integrators
    """
    text = "Привет мир. Это тестовый текст для пайплайна. Нужно проверить задачи."

    response = client.post("/process", json={"text": text})
    assert response.status_code == 200

    data = response.json()

    # Проверяем наличие ключевых полей
    assert "chunks" in data
    assert "summaries" in data
    assert "reduced_summary" in data
    assert "final_summary" in data
    assert "calendar_payload" in data
    assert "jira_payload" in data

    # Проверяем, что summary не пустой
    for summary in data["summaries"]:
        assert len(summary) > 0
    assert len(data["final_summary"]) > 0

    # Проверяем интеграционные payload'ы
    assert "calendar_event" in data["calendar_payload"]
    assert "jira_ticket" in data["jira_payload"]

    # Проверяем наличие задач в Calendar и Jira
    assert len(data["calendar_payload"]["calendar_event"]["tasks"]) > 0
    assert len(data["jira_payload"]["jira_ticket"]["open_items"]) > 0

    # Проверка правильного разбиения текста на чанки
    expected_chunks = [
        "Привет мир",
        "Это тестовый текст для пайплайна",
        "Нужно проверить задачи"
    ]
    assert data["chunks"] == expected_chunks
