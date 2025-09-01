# subscriber.py
import asyncio
import logging
from faststream.nats import NatsBroker

logging.basicConfig(level=logging.INFO)

NATS_URL = "nats://localhost:4222"
PROGRESS_SUBJECT = "meeting.progress"

broker = NatsBroker(NATS_URL)


@broker.subscriber(PROGRESS_SUBJECT)
async def handle_progress(msg):
    print("✅ Получен промежуточный результат:", msg)


async def main():
    try:
        await broker.start()
        print("🚀 Subscriber запущен и слушает тему:", PROGRESS_SUBJECT)

        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logging.exception("Ошибка запуска subscriber:")


if __name__ == "__main__":
    asyncio.run(main())
