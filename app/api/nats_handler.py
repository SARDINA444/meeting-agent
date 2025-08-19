import asyncio
import json
from nats.aio.client import Client as NATS

IN_SUBJECT = "speech.in"
OUT_SUBJECT = "speech.out"
NATS_URL = "nats://nats:4222"   # внутри docker-compose "nats" = имя сервиса


async def run_nats(pipeline):
    """
    Подключение к NATS и обработка сообщений.
    Приходит текст (имитация аудио) → режем на чанки → summary → отправляем обратно.
    """
    nc = NATS()
    await nc.connect(NATS_URL)

    async def message_handler(msg):
        data = msg.data.decode()
        try:
            payload = json.loads(data)
            text = payload.get("text", "")

            # отправляем текст в пайплайн
            chunks = pipeline.process_audio(text)
            summary = pipeline.summarize()

            response = {
                "chunks": chunks,
                "summary": summary,
            }
            await nc.publish(OUT_SUBJECT, json.dumps(response).encode())
        except Exception as e:
            error_msg = {"error": str(e)}
            await nc.publish(OUT_SUBJECT, json.dumps(error_msg).encode())

    # подписываемся на топик
    await nc.subscribe(IN_SUBJECT, cb=message_handler)

    print(f"✅ NATS subscribed to {IN_SUBJECT}, publishing to {OUT_SUBJECT}")
