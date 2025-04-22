# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from assistant.apis.chat_api_base import BaseChatApi
import assistant.impl.apis

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

from assistant.models.extra_models import TokenModel  # noqa: F401
from typing import Any
from assistant.models.chat_completion_request import ChatCompletionRequest
from assistant.models.chat_completion_response import ChatCompletionResponse


router = APIRouter()

ns_pkg = assistant.impl.apis
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/chat/completions",
    responses={
        200: {"model": ChatCompletionResponse, "description": "OK"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Something somewhere went terribly wrong."},
    },
    tags=["chat"],
    response_model_by_alias=True,
)
async def chat_completions(
    chat_completion_request: ChatCompletionRequest = Body(None, description=""),
) -> ChatCompletionResponse:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().chat_completions(chat_completion_request)
