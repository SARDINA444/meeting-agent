from app.reducer.reducer import Reducer
from app.ingest.redis_backend import RedisBackend

def test_reducer_and_redis():
    reducer = Reducer()
    backend = RedisBackend()

    summaries = ["Первый чанк", "Второй чанк"]
    critic_result = {"valid": True, "issues": []}

    for s in summaries:
        reducer.reduce(s, critic_result)

    state = reducer.get_state()
    assert "Первый чанк" in state["rolling_summary"]
    assert "Второй чанк" in state["rolling_summary"]

    # сохраняем
    backend.save_state("test_session", state)

    # восстанавливаем
    restored = backend.load_state("test_session")
    assert restored == state
