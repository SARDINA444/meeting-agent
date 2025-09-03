import redis


class RedisBackend:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)

    def save_intermediate(self, process_id: str, step: int, summary: str):
        key = f"process:{process_id}:step:{step}"
        self.redis.set(key, summary)

    def get_intermediate(self, process_id: str, step: int) -> str | None:
        key = f"process:{process_id}:step:{step}"
        return self.redis.get(key)

    def list_intermediates(self, process_id: str) -> list[str]:
        keys = self.redis.keys(f"process:{process_id}:step:*")
        return [self.redis.get(k) for k in sorted(keys)]
