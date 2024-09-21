# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from base_component_api.apis.component_api_base import BaseComponentApi
import base_component_api.impl
from fastapi import File, UploadFile
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

from base_component_api.models.extra_models import TokenModel  # noqa: F401
from base_component_api.models.chat_response import ChatResponse
from base_component_api.models.key_value import KeyValue


router = APIRouter()

ns_pkg = base_component_api.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/act",
    responses={
        200: {"model": str, "description": "Done"},
        500: {"model": str, "description": "Something Somewhere went terribly wrong."},
        501: {"description": "Not available for this component."},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def act(
    body: str = Body(None, description=""),
) -> str:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().act(body)


@router.post(
    "/question",
    responses={
        200: {"model": ChatResponse, "description": "Answer"},
        404: {"model": str, "description": "Couldn&#39;t answer your question."},
        500: {"model": str, "description": "Something somewhere went terribly wrong."},
        501: {"description": "Doesn&#39;t exist for this component"},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def answer_question(
    body: str = Body(None, description=""),
) -> ChatResponse:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().answer_question(body)


@router.get(
    "/availbale/actions",
    responses={
        200: {"model": List[KeyValue], "description": "Available actions"},
        500: {"model": str, "description": "Something somewhere went terribly wrong"},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def get_available_actions(
) -> List[KeyValue]:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().get_available_actions()


@router.post(
    "/documents",
    responses={
        201: {"description": "Uploading"},
        422: {"model": str, "description": "Unsupoorted document"},
        501: {"description": "Not available for this componment"},
    },
    tags=["component"],
    response_model_by_alias=True,
)
async def upload_document(
    file: UploadFile = File(...)
) -> None:
    if not BaseComponentApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComponentApi.subclasses[0]().upload_document(file)
