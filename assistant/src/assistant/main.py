# coding: utf-8

from contextlib import asynccontextmanager
from fastapi import FastAPI

from assistant.apis.assistant_api import router as assistant_api_router
from assistant.apis.chat_api import router as chat_api_router
from assistant.apis.models_api import router as models_api_router
from assistant.assistant_container import configure
from assistant.endpoints.health_endpoints import router as health_router
from assistant.health.health_check_service import HealthCheckService
from assistant.impl.settings.mcp_server_settings import MCPSettings


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_settings = MCPSettings()
    health_check_service = HealthCheckService(
        check_interval_seconds=mcp_settings.health_check_interval_seconds
    )
    for server in mcp_settings.servers:
        health_check_service.server_health[server.name] = None
    app.state.health_check_service = health_check_service
    health_check_service.start()
    yield
    health_check_service.stop()
    app.state.health_check_service = None


app = FastAPI(
    title="Chat assistant API",
    description="The OpenAI compatible chat assistant REST API.",
    version="2.3.0",
    lifespan=lifespan,
)


app.include_router(chat_api_router)
app.include_router(models_api_router)
app.include_router(assistant_api_router)
app.include_router(health_router)

configure()
