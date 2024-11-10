# coding: utf-8

import importlib
import pkgutil
from typing import Any, Dict, List  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)
from pydantic import StrictStr

import assistant.impl
from assistant.apis.assistant_api_base import BaseAssistantApi
from assistant.models.extra_models import TokenModel  # noqa: F401

router = APIRouter()

ns_pkg = assistant.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/assist",
    responses={
        200: {"model": str, "description": "answer"},
        500: {"description": "Something somewhere went terribly wrong."},
    },
    tags=["assistant"],
    response_model_by_alias=True,
)
async def assist(
    body: StrictStr = Body(None, description=""),
) -> str:
    if not BaseAssistantApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAssistantApi.subclasses[0]().assist(body)
