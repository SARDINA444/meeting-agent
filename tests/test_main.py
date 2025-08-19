import pytest
import httpx

from app.main import app


@pytest.mark.asyncio
async def test_process_and_summary():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # шаг 1: отправляем текст на обработку
        response = await ac.post("/process/", json={"text": "Привет мир из пайплайна"})
        assert response.status_code == 200
        chunks = response.json()["chunks"]
        assert isinstance(chunks, list)
        # проверяем, что слово "Привет" встретилось в каком-то чанке
        assert any("Привет" in chunk for chunk in chunks)

        # шаг 2: получаем summary
        response = await ac.get("/summary/")
        assert response.status_code == 200
        summary = response.json()["summary"]
        assert isinstance(summary, str)
        assert summary != ""
