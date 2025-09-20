import asyncio
import uuid
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

NATS_URL = "nats://localhost:4222"


async def main():
    nc = NATS()
    await nc.connect(servers=[NATS_URL])
    js = nc.jetstream()

    process_id = str(uuid.uuid4())
    chunks = [
        "Первый кусок текста.",
        "Второй кусок текста.",
        "Третий кусок текста."
    ]

    # подписка на промежуточные результаты
    async def progress_handler(msg):
        print("📌 Прогресс:", msg.data.decode())

    await js.subscribe("summaries.progress", cb=progress_handler)

    # подписка на финал
    async def final_handler(msg):
        print("✅ Финал:", msg.data.decode())

    await js.subscribe("summaries.final", cb=final_handler)

    # публикуем задание
    await js.publish("summaries.process", payload={
        "process_id": process_id,
        "chunks": chunks
    }.__str__().encode())

    print(f"🚀 Задача отправлена: {process_id}")

    # держим клиента живым
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
