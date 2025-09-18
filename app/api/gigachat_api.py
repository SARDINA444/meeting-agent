import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_community.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

# Загружаем .env
load_dotenv()

key = os.getenv("GIGA_KEY")

giga = GigaChat(
    credentials=key,
    verify_ssl_certs=False,
    model='GigaChat-2-Pro',
    scope='GIGACHAT_API_B2B'
)


class Text(BaseModel):
    text: str


async def request_to_giga(text: str, system_prompt: str) -> str:
    """
    Асинхронный запрос к GigaChat API для пересказа текста.
    """
    result = await giga.agenerate([[SystemMessage(content=system_prompt), HumanMessage(content=text)]])
    return result.generations[0][0].text


class GigaAgent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    async def run(self, text: str) -> str:
        return await request_to_giga(text, self.system_prompt)
