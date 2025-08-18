import asyncio
from nats.aio.client import Client as NATS
from app.pipeline import process_meeting

NATS_URL = "nats://nats:4222"
IN_SUBJECT = "meeting.in"
OUT_SUBJECT = "meeting.out"


async def run_nats():
    nc = NATS()
    await nc.connect(NATS_URL)

    async def message_handler(msg):
        text = msg.data.decode()

        result = process_meeting(text)
        await nc.publish(OUT_SUBJECT, str(result).encode())

    await nc.subscribe(IN_SUBJECT, cb=message_handler)

    return nc
