from faststream.nats import NatsBroker

IN_SUBJECT = "meeting.in"
OUT_SUBJECT = "meeting.out"
PROGRESS_SUBJECT = "meeting.progress"

# брокер, который будем подключать в main.py
broker = NatsBroker("nats://nats:4222")  # если внутри docker-compose, то хост "nats"
# broker = NatsBroker("nats://localhost:4222")  # если тестируешь локально
