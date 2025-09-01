import pytest
import asyncio
import json
from nats.aio.client import Client as NATS

NATS_URL = "nats://localhost:4222"
IN_SUBJECT = "meeting.in"
PROGRESS_SUBJECT = "meeting.progress"
OUT_SUBJECT = "meeting.out"

@pytest.mark.asyncio
async def test_meeting_pipeline():
    nc = NATS()
    await nc.connect(NATS_URL)

    progress_messages = []
    out_messages = []

    async def progress_handler(msg):
        data = msg.data.decode()
        progress_messages.append(data)
        print("Progress:", data)

    async def out_handler(msg):
        data = msg.data.decode()
        out_messages.append(data)
        print("Final Output:", data)

    await nc.subscribe(PROGRESS_SUBJECT, cb=progress_handler)
    await nc.subscribe(OUT_SUBJECT, cb=out_handler)

    test_chunk = {"chunks": ["Привет, это тестовый чанк для проверки pipeline."]}
    await nc.publish(IN_SUBJECT, json.dumps(test_chunk).encode())

    await asyncio.sleep(5)  # ждём обработку

    assert len(progress_messages) > 0, "Не пришло ни одного промежуточного сообщения"
    assert len(out_messages) > 0, "Не пришёл финальный summary"

    await nc.close()
    print("Test passed!")
