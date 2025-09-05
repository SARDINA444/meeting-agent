import pytest
from fastapi.testclient import TestClient
from app.main import app, compose, broker

client = TestClient(app)

@pytest.mark.asyncio
async def test_process_and_storage(monkeypatch):
    # подключаем брокер вручную (иначе падает)
    await broker.connect()

    # подменяем embeddings, чтобы не ходить в GigaChat
    class DummyEmbeddings:
        def embed_query(self, text: str):
            return [0.5] * 1024

    monkeypatch.setattr("app.main.embeddings", DummyEmbeddings())

    response = client.post("/process/", json={"chunks": ["Hello world", "Second chunk"]})
    assert response.status_code == 200
    data = response.json()

    process_id = data["process_id"]
    final_summary = data["final_summary"]

    intermediates = compose.list_intermediates(process_id)
    assert len(intermediates) == 2

    qdrant_summary = compose.get_final(process_id)
    assert qdrant_summary == final_summary

    # отключаем брокер
    await broker.close()
