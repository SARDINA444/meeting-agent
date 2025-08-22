import redis
import json

class RedisBackend:
    def __init__(self, host="redis", port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def save_state(self, key: str, state: dict):
        self.r.set(key, json.dumps(state))

    def load_state(self, key: str):
        data = self.r.get(key)
        return json.loads(data) if data else None
