# coding: utf-8

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.3.0"}


@router.get("/readiness")
async def readiness():
    """Readiness check endpoint."""
    return {"status": "ready", "version": "2.3.0"}
