import pytest
import asyncio
from nats.aio.client import Client as NATS
from app.pipeline import process_meeting
from app.api.nats_handler import IN_SUBJECT, OUT_SUBJECT, NATS_URL, run_nats

@pytest.mark.asyncio
async def test_nats_pipeline():
    # Запускаем NATS клиент для теста
    nc = NATS()
    await nc.connect(NATS_URL)

    # Запускаем подписку пайплайна (имитация старта сервиса)
    asyncio.create_task(run_nats())

    # Future для результата
    future = asyncio.get_event_loop().create_future()

    async def message_handler(msg):
        result = msg.data.decode()
        future.set_result(result)

    await nc.subscribe(OUT_SUBJECT, cb=message_handler)

    # Отправляем тестовое сообщение
    await nc.publish(IN_SUBJECT, b"hello from test")

    # Ждём ответа (не более 3 секунд)
    result = await asyncio.wait_for(future, timeout=3)

    # Проверяем
    assert "HELLO FROM TEST" in result
    await nc.close()
