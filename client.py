import asyncio
import json
import uuid
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    await nc.connect("nats://localhost:4222")

    file_id = str(uuid.uuid4())
    total_chunks = 3

    # для отслеживания полученных сообщений
    received_chunks = {}
    final_summary = None
    done_event = asyncio.Event()

    async def message_handler(msg):
        nonlocal final_summary
        data = json.loads(msg.data.decode())
        if data.get("file_id") != file_id:
            return

        if "chunk_index" in data:
            # intermediate
            received_chunks[data["chunk_index"]] = data["summary"]
        elif "final_summary" in data:
            # final
            final_summary = data["final_summary"]

        # если получили все intermediate + final, устанавливаем событие
        if len(received_chunks) == total_chunks and final_summary is not None:
            done_event.set()

        # печать с нормальными буквами
        print(json.dumps(data, indent=2, ensure_ascii=False))

    # подписываемся
    await nc.subscribe("summaries.intermediate", cb=message_handler)
    await nc.subscribe("summaries.final", cb=message_handler)

    # отправляем чанки
    text_chunks = [
        "Иван: Добрый день, Николай. Хотел бы обсудить стратегию формирования бюджета на следующий квартал. У нас есть несколько ключевых направлений, которые требуют внимания и финансирования, чтобы обеспечить рост и развитие компании.",
        "Николай: Добрый день, Иван. Конечно, давайте вместе посмотрим на основные статьи расходов и приоритеты. Какие направления вы считаете наиболее важными для этого периода?",
        "Иван: В первую очередь, необходимо увеличить инвестиции в маркетинг, чтобы расширить присутствие бренда на рынке и привлечь новых клиентов. Также планируем обновить оборудование в производственном цехе для повышения эффективности и качества продукции. Не менее важно — инвестировать в обучение сотрудников, чтобы повысить их профессиональный уровень и мотивацию.",
    ]

    for i, text in enumerate(text_chunks):
        await nc.publish("summaries.process", json.dumps({
            "file_id": file_id,
            "chunk_index": i,
            "total_chunks": len(text_chunks),
            "text": text
        }).encode())

    # ждём, пока все сообщения придут
    await done_event.wait()
    await nc.close()

asyncio.run(main())
