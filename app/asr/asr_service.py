from app.summarizer.summarizer import simple_summarizer, critic
from app.reducer.reducer import Reducer
from ..ingest.redis_backend import RedisBackend

reducer = Reducer()
state_backend = RedisBackend()

def process_chunks(chunks: list[str], state_key="session1"):
    for chunk in chunks:
        # делаем summary для чанка
        summary = simple_summarizer([chunk], max_len=100)

        # проверяем Critic
        critic_result = critic(summary)

        # обновляем Reducer
        rolling_summary = reducer.reduce(summary, critic_result)

        # сохраняем состояние
        state_backend.save_state(state_key, reducer.get_state())

    # итоговое состояние
    return reducer.get_state()
