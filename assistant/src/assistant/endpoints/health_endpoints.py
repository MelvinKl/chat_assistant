# coding: utf-8

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from assistant.health import HealthCheckService

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    """Health check endpoint."""
    health_check_service: HealthCheckService = request.app.state.health_check_service

    is_healthy = health_check_service.get_overall_health()

    if is_healthy:
        return JSONResponse(status_code=200, content={"status": "healthy", "version": "2.3.0"})

    servers = []
    for server_name, status in health_check_service.server_health.items():
        if status is not None:
            server_detail = {
                "name": server_name,
                "healthy": status.healthy,
                "last_checked": status.last_checked.isoformat() if status.last_checked else None,
            }
            if status.error_message:
                server_detail["error"] = status.error_message
            servers.append(server_detail)

    return JSONResponse(status_code=503, content={"status": "unhealthy", "version": "2.3.0", "servers": servers})


@router.get("/readiness")
async def readiness(request: Request):
    """Readiness check endpoint."""
    health_check_service: HealthCheckService = request.app.state.health_check_service

    is_healthy = health_check_service.get_overall_health()

    if is_healthy:
        return JSONResponse(status_code=200, content={"status": "ready", "version": "2.3.0"})

    return JSONResponse(status_code=503, content={"status": "not ready", "version": "2.3.0"})
