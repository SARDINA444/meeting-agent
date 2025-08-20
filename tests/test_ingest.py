import pytest
from app.ingest.redis_backend import RedisBackend


@pytest.fixture
def backend():
    return RedisBackend("redis://redis:6379/0")  # из docker-compose


def test_save_and_load_state(backend):
    key = "meeting:123"
    state = {"chunks": ["привет", "мир"], "summary": "привет мир"}

    backend.save_state(key, state)
    loaded = backend.load_state(key)

    assert loaded == state


def test_delete_state(backend):
    key = "meeting:delete"
    state = {"chunks": ["удалить"], "summary": "удаление"}

    backend.save_state(key, state)
    backend.delete_state(key)
    loaded = backend.load_state(key)

    assert loaded is None
