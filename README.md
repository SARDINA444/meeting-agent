# Meeting Agent

## Быстрый запуск

Поднять контейнеры

```bash
docker-compose up --build
```
## Запуск уже созданных контейнеров

```bash
docker-compose up
```

## Тесты
```bash
docker-compose exec app pytest tests/test_pipeline.py -v
```
