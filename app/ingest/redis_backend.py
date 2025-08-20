import os
import json
import redis


class RedisBackend:
    def __init__(self, url: str | None = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.url, decode_responses=True)

    def save_state(self, key: str, state: dict) -> None:
        """
        Сохраняем состояние (dict) в Redis по ключу
        """
        self.client.set(key, json.dumps(state))

    def load_state(self, key: str) -> dict | None:
        """
        Загружаем состояние из Redis по ключу
        """
        raw = self.client.get(key)
        return json.loads(raw) if raw else None

    def delete_state(self, key: str) -> None:
        """
        Удаляем состояние
        """
        self.client.delete(key)
