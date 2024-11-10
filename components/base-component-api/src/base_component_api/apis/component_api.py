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
    UploadFile,
    status,
)
from pydantic import StrictStr

import base_component_api.impl
from base_component_api.apis.component_api_base import BaseComponentApi
from base_component_api.models.chat_response import ChatResponse
from base_component_api.models.description import Description
from base_component_api.models.extra_models import TokenModel  # noqa: F401

router = APIRouter()

ns_pkg = base_component_api.impl
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
        200: {"model": Description, "description": "Available actions"},
        500: {"model": str, "description": "Something somewhere went terribly wrong"},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def get_description() -> Description:
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
    file: UploadFile,
) -> None:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().upload_document(file)
