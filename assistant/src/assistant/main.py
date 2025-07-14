# coding: utf-8


from fastapi import FastAPI

from assistant.apis.chat_api import router as chat_api_router
from assistant.apis.models_api import router as models_api_router
from assistant.assistant_container import configure

app = FastAPI(
    title="Chat assistant API",
    description="The OpenAI compatible chat assistant REST API.",
    version="2.3.0",
)


app.include_router(chat_api_router)
app.include_router(models_api_router)


configure()
