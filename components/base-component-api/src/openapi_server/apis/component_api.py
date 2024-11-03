# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.component_api_base import BaseComponentApi
import openapi_server.impl

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

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import StrictStr
from typing import Any, List
from openapi_server.models.chat_response import ChatResponse
from openapi_server.models.key_value import KeyValue


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/assist",
    responses={
        200: {"model": ChatResponse, "description": "Answer"},
        404: {"model": str, "description": "Couldn&#39;t answer your question."},
        500: {"model": str, "description": "Something somewhere went terribly wrong."},
        501: {"description": "Doesn&#39;t exist for this component"},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def assist(
    body: StrictStr = Body(None, description=""),
) -> ChatResponse:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().assist(body)


@router.get(
    "/description",
    responses={
        200: {"model": List[KeyValue], "description": "Available actions"},
        500: {"model": str, "description": "Something somewhere went terribly wrong"},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def get_description(
) -> List[KeyValue]:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().get_description()


@router.post(
    "/documents",
    responses={
        201: {"description": "Uploading"},
        422: {"model": str, "description": "Unsuported document"},
        501: {"description": "Not available for this componment"},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def upload_document(
) -> None:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().upload_document()
