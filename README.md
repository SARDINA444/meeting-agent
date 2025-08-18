# Meeting Agent

## Быстрый запуск

Поднять два контейнера — FastAPI-сервис и брокер сообщений NATS

```bash
docker-compose up --build
```

## Тесты
```bash
docker-compose exec app pytest tests/test_nats.py -v
```
## Запуск уже созданных контейнеров

```bash
docker-compose up
```