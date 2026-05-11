"""
Mock MCP Server for Testing

This is a lightweight mock MCP server that provides simple test tools
without requiring a full LLM backend.
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import FastAPI
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
    """Handle JSON-RPC requests."""
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
            content = [
                {"type": "text", "text": f"Current time in {timezone}: 12:00 PM"}
            ]
        else:
            content = [{"type": "text", "text": f"Unknown tool: {tool_name}"}]

        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {"content": content, "isError": False},
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "error": {"code": -32601, "message": "Method not found"},
        }


@app.get("/sse")
async def sse_endpoint():
    """SSE endpoint for MCP server communication."""

    async def event_generator():
        request_queue = asyncio.Queue()
        response_queue = asyncio.Queue()

        async def handle_messages():
            while True:
                try:
                    data = await asyncio.wait_for(request_queue.get(), timeout=5.0)
                    if data is None:
                        break
                    request = JSONRPCRequest(**json.loads(data))
                    response = await handle_request(request)
                    await response_queue.put(json.dumps(response))
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {"event": "keepalive", "data": ""}
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

        # Start message handler
        handler = asyncio.create_task(handle_messages())

        # Yield initial responses
        try:
            init_request = JSONRPCRequest(id=1, method="initialize", params={})
            init_response = await handle_request(init_request)
            yield {"data": json.dumps(init_response)}

            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            }
            yield {"data": json.dumps(initialized_notification)}

            # Handle any pending responses
            while not response_queue.empty():
                response = await response_queue.get()
                yield {"data": response}

            # Keep the connection alive
            while True:
                await asyncio.sleep(1)
                yield {"event": "keepalive", "data": ""}
        except Exception as e:
            logger.error(f"SSE error: {e}")
        finally:
            handler.cancel()

    return EventSourceResponse(event_generator())


@app.post("/")
async def jsonrpc_endpoint(request: JSONRPCRequest):
    """Handle JSON-RPC POST requests."""
    response = await handle_request(request)
    return response


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
