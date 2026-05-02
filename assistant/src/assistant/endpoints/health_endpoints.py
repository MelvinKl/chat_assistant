# coding: utf-8

import logging

from fastapi import APIRouter
from langchain_mcp_adapters.client import MultiServerMCPClient

from assistant.impl.settings.mcp_server_settings import load_mcp_settings_from_json

router = APIRouter()
logger = logging.getLogger(__name__)


async def _check_mcp_servers_tool_availability() -> tuple[bool, list[str]]:
    """Check that all configured MCP servers return at least one tool."""
    settings_mcp = load_mcp_settings_from_json()
    failed_servers: list[str] = []

    for server_definition in settings_mcp.servers:
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
        mcp_client = MultiServerMCPClient(server_dict)
        try:
            server_tools = await mcp_client.get_tools()
            if not server_tools:
                logger.warning("MCP server %s returned no tools", server_definition.name)
                failed_servers.append(server_definition.name)
        except Exception as e:
            logger.error("Could not connect to MCP server %s: %s", server_definition.name, e)
            failed_servers.append(server_definition.name)

    return len(failed_servers) == 0, failed_servers


@router.get("/health")
async def health():
    """Health check endpoint."""
    is_healthy, failed_servers = await _check_mcp_servers_tool_availability()
    if not is_healthy:
        return {"status": "unhealthy", "version": "2.3.0", "failed_servers": failed_servers}
    return {"status": "healthy", "version": "2.3.0"}


@router.get("/readiness")
async def readiness():
    """Readiness check endpoint."""
    is_ready, failed_servers = await _check_mcp_servers_tool_availability()
    if not is_ready:
        return {"status": "not ready", "version": "2.3.0", "failed_servers": failed_servers}
    return {"status": "ready", "version": "2.3.0"}
