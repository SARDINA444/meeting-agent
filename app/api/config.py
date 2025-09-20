from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # NATS / FastStream
    nats_servers: str = Field("nats://nats:4222", env="NATS_SERVERS")
    nats_subject_in: str = Field("summaries.process", env="NATS_SUBJECT_IN")
    nats_subject_intermediate: str = Field("summaries.intermediate", env="NATS_SUBJECT_INTERMEDIATE")
    nats_subject_final: str = Field("summaries.final", env="NATS_SUBJECT_FINAL")

    # Redis
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")

    # Qdrant
    qdrant_url: str = Field("http://qdrant:6333", env="QDRANT_URL")

    # GigaChat
    giga_key: str = Field(..., env="GIGA_KEY")


settings = Settings()
