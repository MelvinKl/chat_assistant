# coding: utf-8

from fastapi import FastAPI

from assistant.apis.assistant_api import router as assistant_api_router
from assistant.apis.chat_api import router as chat_api_router
from assistant.apis.models_api import router as models_api_router
from assistant.assistant_container import configure
from assistant.endpoints.health_endpoints import router as health_router

app = FastAPI(
    title="Chat assistant API",
    description="The OpenAI compatible chat assistant REST API.",
    version="2.3.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": app.version}


@app.get("/readiness")
def readiness_check():
    return {"status": "ready", "version": app.version}


app.include_router(chat_api_router)
app.include_router(models_api_router)
app.include_router(assistant_api_router)
app.include_router(health_router)

configure()
