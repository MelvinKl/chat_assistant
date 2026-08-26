"""
Mock MCP Server for Testing

A lightweight mock server that implements the MCP (Model Context Protocol)
SSE transport and provides simple test tools, without requiring a real MCP
tool backend.

Protocol (per MCP SSE transport spec):
  1. The client opens GET /sse.
  2. The server sends an `endpoint` event containing the URL to POST
     JSON-RPC messages to.
  3. The client POSTs JSON-RPC requests to that URL; the server sends the
     corresponding JSON-RPC responses back on the SSE stream.
"""

import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str | None = None
    method: str
    params: dict[str, Any] | None = None


# Mock tools that the server provides
MOCK_TOOLS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude coordinate"},
                "longitude": {"type": "number", "description": "Longitude coordinate"},
            },
            "required": ["latitude", "longitude"],
        },
    },
    {
        "name": "get_time",
        "description": "Get the current time",
        "inputSchema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone (e.g., UTC, America/New_York)",
                }
            },
        },
    },
]


async def handle_request(request: JSONRPCRequest):
    """Handle a JSON-RPC request and return the JSON-RPC response as a dict."""
    logger.info(f"Received request: {request.method}")

    if request.method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "mock-mcp-server", "version": "1.0.0"},
                "capabilities": {
                    "tools": {"listChanged": True},
                },
            },
        }
    elif request.method in ("notifications/initialized", "initialized"):
        # Notification: no response required
        return None
    elif request.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {"tools": MOCK_TOOLS},
        }
    elif request.method == "tools/call":
        tool_name = request.params.get("name") if request.params else None
        arguments = request.params.get("arguments", {}) if request.params else {}

        logger.info(f"Tool call: {tool_name} with args: {arguments}")

        if tool_name == "get_weather":
            content = [
                {
                    "type": "text",
                    "text": f"Weather at lat={arguments.get('latitude')}, lon={arguments.get('longitude')}: Sunny, 22°C",
                }
            ]
        elif tool_name == "get_time":
            timezone = arguments.get("timezone", "UTC")
            content = [{"type": "text", "text": f"Current time in {timezone}: 12:00 PM"}]
        else:
            content = [{"type": "text", "text": f"Unknown tool: {tool_name}"}]

        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {"content": content, "isError": False},
        }
    else:
        if request.id is None:
            # Unknown notification: no response required
            return None
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "error": {"code": -32601, "message": "Method not found"},
        }


# Session id -> queue of JSON strings to be sent over the SSE stream
SESSIONS: dict[str, asyncio.Queue] = {}


@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP server communication."""
    session_id = uuid.uuid4().hex
    queue: asyncio.Queue = asyncio.Queue()
    SESSIONS[session_id] = queue

    async def event_generator():
        try:
            # Per the MCP SSE transport spec, the first event must be the
            # `endpoint` event pointing at the URL to POST messages to.
            yield {
                "event": "endpoint",
                "data": f"/messages?session_id={session_id}",
            }
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {"data": message}
                except asyncio.TimeoutError:
                    # Keepalive comment so the connection stays alive
                    yield {"event": "keepalive", "data": ""}
        finally:
            SESSIONS.pop(session_id, None)

    return EventSourceResponse(event_generator())


@app.post("/messages")
async def messages_endpoint(request: Request):
    """Receive JSON-RPC messages and send responses back over the SSE stream."""
    session_id = request.query_params.get("session_id")
    queue = SESSIONS.get(session_id)
    if queue is None:
        raise HTTPException(status_code=404, detail="Unknown session")

    raw = await request.body()
    try:
        jsonrpc_request = JSONRPCRequest(**json.loads(raw))
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON-RPC request: {e}")

    response = await handle_request(jsonrpc_request)
    if response is not None:
        await queue.put(json.dumps(response))

    # Per the MCP SSE transport spec, the POST response is 202 Accepted and
    # the actual result is delivered over the SSE stream.
    return {"status": "accepted"}, 202


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "mock-mcp-server",
        "version": "1.0.0",
        "description": "Mock MCP Server for Testing",
        "tools": [tool["name"] for tool in MOCK_TOOLS],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
