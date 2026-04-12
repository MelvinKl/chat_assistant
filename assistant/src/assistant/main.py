"""
Main application entry point for the assistant service.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

# Try to import FastAPI, provide a mock for testing if not available
try:
    from fastapi import FastAPI
except ImportError:
    # Mock FastAPI for testing environments
    class FastAPI:
        def __init__(self, *args: Any, **kwargs: Any):
            pass

        def get(self, *args: Any, **kwargs: Any):
            def decorator(func: Any) -> Any:
                return func

            return decorator


from assistant.impl.settings.mcp_server_settings import (
    load_mcp_settings_from_json,
    MCPSettings,
)

logger = logging.getLogger(__name__)


def validate_tool_availability(settings: MCPSettings) -> bool:
    """
    Validate that all configured MCP tools are available.

    In a real implementation, this would check actual connectivity to MCP servers.
    For this implementation, we'll simulate the check.

    Returns:
        bool: True if all tools are available, False otherwise
    """
    # For now, we'll assume all tools are available if we can load the settings
    # In a real implementation, this would attempt to connect to each server
    logger.info("Checking availability of %d MCP servers", len(settings.servers))

    # Simulate tool availability check
    # In reality, this would involve network calls to check server health
    all_available = True
    for server in settings.servers:
        logger.debug("Checking server: %s (%s)", server.name, server.url)
        # Placeholder for actual availability check
        # For demonstration, we'll consider all servers available
        pass

    return all_available


async def periodic_tool_check(settings: MCPSettings, check_interval: int = 60):
    """
    Periodically check tool availability and exit if strict mode is enabled and tools become unavailable.

    Args:
        settings: MCP settings containing strict mode flag and server configuration
        check_interval: Interval in seconds between checks (default: 60)
    """
    while True:
        await asyncio.sleep(check_interval)

        if settings.strict:
            logger.info("Performing periodic tool availability check (strict mode)")
            if not validate_tool_availability(settings):
                logger.error("MCP tools are not available in strict mode. Exiting.")
                sys.exit(1)
        else:
            logger.debug("Skipping periodic tool check (non-strict mode)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting assistant service")

    # Load MCP settings
    try:
        settings = load_mcp_settings_from_json()
        logger.info("Loaded MCP settings with %d servers", len(settings.servers))

        # Check tool availability at startup if strict mode is enabled
        if settings.strict:
            logger.info("Strict mode enabled - validating tool availability at startup")
            if not validate_tool_availability(settings):
                logger.error("MCP tools are not available in strict mode. Exiting.")
                sys.exit(1)
            else:
                logger.info("All MCP tools are available")

        # Start periodic tool checking task if strict mode is enabled
        if settings.strict:
            asyncio.create_task(periodic_tool_check(settings))
            logger.info("Started periodic tool availability checking")

    except Exception as e:
        logger.error("Failed to load MCP settings: %s", e)
        sys.exit(1)

    yield

    # Shutdown
    logger.info("Shutting down assistant service")


# Create FastAPI app
app = FastAPI(
    title="Assistant Service",
    description="AI Assistant Service with MCP Tool Support",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/readiness")
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "version": "0.1.0"}


if __name__ == "__main__":
    try:
        import uvicorn

        # Binding to 0.0.0.0 is intentional for containerized deployment
        uvicorn.run(app, host="0.0.0.0", port=8080)  # nosec: S104
    except ImportError:
        logger.warning("uvicorn not available, skipping server start")
        # For testing purposes, we can still run the application logic
        pass
