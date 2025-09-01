import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_process_chunks():
    test_data = {
        "chunks": [
            "Первый чанк текста о проекте.",
            "Второй чанк с дополнительной информацией."
        ]
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/process/", json=test_data)

    assert response.status_code == 200
    data = response.json()
    assert "final_summary" in data
    assert isinstance(data["final_summary"], str)
