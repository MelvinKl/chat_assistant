# coding: utf-8

import asyncio
import logging
import threading
import time
from enum import StrEnum
from threading import Lock

import inject
from fastapi import APIRouter
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mcp_adapters.client import MultiServerMCPClient

from assistant.impl.mcp_sampling import create_sampling_callback
from assistant.impl.settings.mcp_server_settings import MCPSettings

logger = logging.getLogger(__name__)
router = APIRouter()


lock = Lock()


class Status(StrEnum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


status = Status.HEALTHY
health_thread = None


def _probe_server(server_definition, sampling_callback):
    """The mcp client with which one health-probe round reaches one server."""
    server_dict = {}
    if server_definition.transport == "stdio":
        server_dict[server_definition.name] = {
            "command": server_definition.command,
            "args": server_definition.args,
            "transport": "stdio",
        }
    else:
        server_dict[server_definition.name] = {
            "url": server_definition.url,
            "transport": server_definition.transport,
        }
        if server_definition.headers:
            server_dict[server_definition.name]["headers"] = server_definition.headers
    if sampling_callback is not None:
        server_dict[server_definition.name]["session_kwargs"] = {"sampling_callback": sampling_callback}
    return MultiServerMCPClient(server_dict)


@inject.params(
    mcp_settings=MCPSettings,
    tools="tools",
    llm=BaseChatModel,
)
def health_check(mcp_settings, tools, llm=None):
    global status
    sampling_callback = create_sampling_callback(llm) if llm is not None else None
    while True:
        for server_definition in mcp_settings.servers:
            logger.info("Checking mcp-server %s" % server_definition.name)
            mcp_client = _probe_server(server_definition, sampling_callback)
            try:
                server_tools = asyncio.run(mcp_client.get_tools())
                if server_definition.agent not in tools:
                    tools[server_definition.agent] = []
                tools[server_definition.agent] += server_tools
            except Exception:
                with lock:
                    status = Status.UNHEALTHY
        time.sleep(300)


@router.get("/health")
async def health():
    """Health check endpoint."""
    global health_thread
    if not health_thread:
        health_thread = threading.Thread(target=health_check)
        health_thread.start()
    with lock:
        return {"status": status.value, "version": "2.3.0"}


@router.get("/readiness")
async def readiness():
    """Readiness check endpoint."""
    return {"status": "ready", "version": "2.3.0"}
