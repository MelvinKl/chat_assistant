import importlib
import pkgutil

from fastapi import APIRouter, Body, HTTPException

import assistant.impl.apis
from assistant.apis.chat_api_base import BaseChatApi
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
