# Meeting Agent

## Быстрый запуск

Создайте `.env` файл
```bash
echo "GIGA_KEY=<ваш-api-ключ>" >> .env
```

Соберите и запустите сервис

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
