import asyncio
import json
import uuid
from nats.aio.client import Client as NATS

NATS_URL = "nats://localhost:4222"  # если сервис в Docker, использовать имя контейнера: nats://nats:4222
SUBJECT_IN = "summaries.process"
SUBJECT_INTERMEDIATE = "summaries.intermediate"
SUBJECT_FINAL = "summaries.final"

async def main():
    nc = NATS()
    await nc.connect(servers=[NATS_URL])

    # Подписка на промежуточные саммари
    async def intermediate_handler(msg):
        data = json.loads(msg.data.decode())
        print("📌 Intermediate summary:", json.dumps(data, ensure_ascii=False, indent=2))

    await nc.subscribe(SUBJECT_INTERMEDIATE, cb=intermediate_handler)

    # Подписка на финальные саммари
    async def final_handler(msg):
        data = json.loads(msg.data.decode())
        print("✅ Final summary:", json.dumps(data, ensure_ascii=False, indent=2))

    await nc.subscribe(SUBJECT_FINAL, cb=final_handler)

    # Генерируем file_id
    file_id = str(uuid.uuid4())

    # Пример текста, разбиваем на чанки
    text_chunks = [
        "Иван: Добрый день, Николай. Хотел бы обсудить стратегию формирования бюджета на следующий квартал. У нас есть несколько ключевых направлений, которые требуют внимания и финансирования, чтобы обеспечить рост и развитие компании.",
        "Николай: Добрый день, Иван. Конечно, давайте вместе посмотрим на основные статьи расходов и приоритеты. Какие направления вы считаете наиболее важными для этого периода?",
        "Иван: В первую очередь, необходимо увеличить инвестиции в маркетинг, чтобы расширить присутствие бренда на рынке и привлечь новых клиентов. Также планируем обновить оборудование в производственном цехе для повышения эффективности и качества продукции. Не менее важно — инвестировать в обучение сотрудников, чтобы повысить их профессиональный уровень и мотивацию.",
    ]

    # Отправляем чанки по порядку
    for idx, chunk in enumerate(text_chunks):
        msg = {
            "file_id": file_id,
            "chunk_index": idx,
            "total_chunks": len(text_chunks),
            "text": chunk
        }
        await nc.publish(SUBJECT_IN, json.dumps(msg).encode())
        await asyncio.sleep(0.1)  # небольшая пауза, чтобы сервис успел обработать

    print(f"Все чанки отправлены, file_id={file_id}")
    # Даем время на обработку финального summary
    await asyncio.sleep(5)

    await nc.close()

if __name__ == "__main__":
    asyncio.run(main())
