import asyncio
import json
import pytest
from nats.aio.client import Client as NATS

from app.pipeline import MeetingPipeline
from app.api.nats_handler import run_nats

IN_SUBJECT = "speech.in"
OUT_SUBJECT = "speech.out"
NATS_URL = "nats://nats:4222"   # тот же URL, что и в nats_handler.py


@pytest.mark.asyncio
async def test_nats_pipeline():
    """
    Тест проверяет, что сообщение, отправленное в speech.in,
    проходит через pipeline и возвращает summary в speech.out.
    """
    pipeline = MeetingPipeline()
    nc = NATS()
    await nc.connect(NATS_URL)

    # запускаем run_nats в фоне
    asyncio.create_task(run_nats(pipeline))

    # future для ответа
    response_future = asyncio.get_event_loop().create_future()

    async def response_handler(msg):
        response = json.loads(msg.data.decode())
        response_future.set_result(response)

    # подписываемся на выходной топик
    await nc.subscribe(OUT_SUBJECT, cb=response_handler)

    # публикуем тестовое сообщение
    payload = {"text": "Привет мир"}
    await nc.publish(IN_SUBJECT, json.dumps(payload).encode())

    # ждём ответа
    response = await asyncio.wait_for(response_future, timeout=3)

    await nc.close()

    assert "chunks" in response
    assert "summary" in response
    assert response["summary"] != ""
