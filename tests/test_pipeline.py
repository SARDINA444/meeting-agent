import pytest
from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path

client = TestClient(app)


@pytest.fixture
def mock_audio_file(tmp_path):
    """
    Fixture создаёт тестовый текстовый файл, имитирующий аудиофайл.
    """
    file_path = tmp_path / "mock_audio.txt"
    file_path.write_text(
        "Привет мир. Это тестовый файл для пайплайна. Нужно проверить задачи."
    )
    return str(file_path)


def test_process_pipeline(mock_audio_file):
    """
    Проверяем полный пайплайн:
    - транскрипция (ASR)
    - суммаризация
    - редьюсер
    - финализатор
    - интеграторы Calendar/Jira
    """
    response = client.post("/process", json={"audio_path": mock_audio_file})
    assert response.status_code == 200

    data = response.json()

    # Проверяем наличие основных полей
    assert "transcription" in data
    assert "chunks" in data
    assert "summaries" in data
    assert "reduced_summary" in data
    assert "final_summary" in data
    assert "calendar_payload" in data
    assert "jira_payload" in data

    # Проверяем, что summary не пустой
    assert len(data["final_summary"]) > 0

    # Проверяем интеграционные payload'ы
    assert "calendar_event" in data["calendar_payload"]
    assert "jira_ticket" in data["jira_payload"]

    # Правильный доступ к задачам
    assert len(data["calendar_payload"]["calendar_event"]["tasks"]) > 0
    assert len(data["jira_payload"]["jira_ticket"]["open_items"]) > 0
