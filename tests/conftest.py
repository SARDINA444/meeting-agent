import pytest
import time
from app.ingest.redis_backend import RedisBackend
from app.ingest.qdrant_backend import QdrantBackend

REDIS_URL = "redis://redis:6379/0"
QDRANT_URL = "http://qdrant:6333"

@pytest.fixture(scope="session")
def redis_backend():
    backend = RedisBackend(redis_url=REDIS_URL)
    backend.redis.flushdb()
    return backend

@pytest.fixture(scope="session")
def qdrant_backend():
    backend = QdrantBackend(qdrant_url=QDRANT_URL, vector_size=1024)
    time.sleep(1)  # ждём пока поднимется Qdrant
    return backend
