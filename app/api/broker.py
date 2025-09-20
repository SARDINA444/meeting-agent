from faststream import FastStream
from faststream.nats import NatsBroker
from .config import settings

broker = NatsBroker(servers=settings.nats_servers)
app = FastStream(broker)
