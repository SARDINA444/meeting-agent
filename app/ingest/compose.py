import os
from .redis_backend import RedisBackend
# from ingest.qdrant_backend import QdrantBackend  # позже подключим

def get_backend():
    backend_type = os.getenv("STATE_BACKEND", "redis")

    if backend_type == "redis":
        return RedisBackend()
    # elif backend_type == "qdrant":
    #     return QdrantBackend()
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
