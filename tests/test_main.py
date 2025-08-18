from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_process():
    response = client.post("/api/process/", json={"text": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"] == "HELLO"
