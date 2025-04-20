# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from assistant.apis.chat_api_base import BaseChatApi
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

from assistant.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictInt, StrictStr, field_validator
from typing import Dict, Optional
from typing_extensions import Annotated
from assistant.models.chat_completion_deleted import ChatCompletionDeleted
from assistant.models.chat_completion_list import ChatCompletionList
from assistant.models.chat_completion_message_list import ChatCompletionMessageList
from assistant.models.create_chat_completion_request import CreateChatCompletionRequest
from assistant.models.create_chat_completion_response import CreateChatCompletionResponse
from assistant.models.update_chat_completion_request import UpdateChatCompletionRequest
from assistant.security_api import get_token_ApiKeyAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/chat/completions",
    responses={
        200: {"model": CreateChatCompletionResponse, "description": "OK"},
    },
    tags=["Chat"],
    summary="**Starting a new project?** We recommend trying [Responses](/docs/api-reference/responses)  to take advantage of the latest OpenAI platform features. Compare [Chat Completions with Responses](/docs/guides/responses-vs-chat-completions?api-mode&#x3D;responses).  ---  Creates a model response for the given chat conversation. Learn more in the [text generation](/docs/guides/text-generation), [vision](/docs/guides/vision), and [audio](/docs/guides/audio) guides.  Parameter support can differ depending on the model used to generate the response, particularly for newer reasoning models. Parameters that are only supported for reasoning models are noted below. For the current state of  unsupported parameters in reasoning models,  [refer to the reasoning guide](/docs/guides/reasoning). ",
    response_model_by_alias=True,
)
async def create_chat_completion(
    create_chat_completion_request: CreateChatCompletionRequest = Body(None, description=""),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> CreateChatCompletionResponse:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().create_chat_completion(create_chat_completion_request)


@router.delete(
    "/chat/completions/{completion_id}",
    responses={
        200: {"model": ChatCompletionDeleted, "description": "The chat completion was deleted successfully."},
    },
    tags=["Chat"],
    summary="Delete a stored chat completion. Only Chat Completions that have been created with the &#x60;store&#x60; parameter set to &#x60;true&#x60; can be deleted. ",
    response_model_by_alias=True,
)
async def delete_chat_completion(
    completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to delete.")] = Path(..., description="The ID of the chat completion to delete."),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> ChatCompletionDeleted:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().delete_chat_completion(completion_id)


@router.get(
    "/chat/completions/{completion_id}",
    responses={
        200: {"model": CreateChatCompletionResponse, "description": "A chat completion"},
    },
    tags=["Chat"],
    summary="Get a stored chat completion. Only Chat Completions that have been created with the &#x60;store&#x60; parameter set to &#x60;true&#x60; will be returned. ",
    response_model_by_alias=True,
)
async def get_chat_completion(
    completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to retrieve.")] = Path(..., description="The ID of the chat completion to retrieve."),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> CreateChatCompletionResponse:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().get_chat_completion(completion_id)


@router.get(
    "/chat/completions/{completion_id}/messages",
    responses={
        200: {"model": ChatCompletionMessageList, "description": "A list of messages"},
    },
    tags=["Chat"],
    summary="Get the messages in a stored chat completion. Only Chat Completions that have been created with the &#x60;store&#x60; parameter set to &#x60;true&#x60; will be returned. ",
    response_model_by_alias=True,
)
async def get_chat_completion_messages(
    completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to retrieve messages from.")] = Path(..., description="The ID of the chat completion to retrieve messages from."),
    after: Annotated[Optional[StrictStr], Field(description="Identifier for the last message from the previous pagination request.")] = Query(None, description="Identifier for the last message from the previous pagination request.", alias="after"),
    limit: Annotated[Optional[StrictInt], Field(description="Number of messages to retrieve.")] = Query(20, description="Number of messages to retrieve.", alias="limit"),
    order: Annotated[Optional[StrictStr], Field(description="Sort order for messages by timestamp. Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.")] = Query(asc, description="Sort order for messages by timestamp. Use &#x60;asc&#x60; for ascending order or &#x60;desc&#x60; for descending order. Defaults to &#x60;asc&#x60;.", alias="order"),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> ChatCompletionMessageList:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().get_chat_completion_messages(completion_id, after, limit, order)


@router.get(
    "/chat/completions",
    responses={
        200: {"model": ChatCompletionList, "description": "A list of Chat Completions"},
    },
    tags=["Chat"],
    summary="List stored Chat Completions. Only Chat Completions that have been stored with the &#x60;store&#x60; parameter set to &#x60;true&#x60; will be returned. ",
    response_model_by_alias=True,
)
async def list_chat_completions(
    model: Annotated[Optional[StrictStr], Field(description="The model used to generate the Chat Completions.")] = Query(None, description="The model used to generate the Chat Completions.", alias="model"),
    metadata: Annotated[Optional[Dict[str, StrictStr]], Field(description="A list of metadata keys to filter the Chat Completions by. Example:  `metadata[key1]=value1&metadata[key2]=value2` ")] = Query(None, description="A list of metadata keys to filter the Chat Completions by. Example:  &#x60;metadata[key1]&#x3D;value1&amp;metadata[key2]&#x3D;value2&#x60; ", alias="metadata"),
    after: Annotated[Optional[StrictStr], Field(description="Identifier for the last chat completion from the previous pagination request.")] = Query(None, description="Identifier for the last chat completion from the previous pagination request.", alias="after"),
    limit: Annotated[Optional[StrictInt], Field(description="Number of Chat Completions to retrieve.")] = Query(20, description="Number of Chat Completions to retrieve.", alias="limit"),
    order: Annotated[Optional[StrictStr], Field(description="Sort order for Chat Completions by timestamp. Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.")] = Query(asc, description="Sort order for Chat Completions by timestamp. Use &#x60;asc&#x60; for ascending order or &#x60;desc&#x60; for descending order. Defaults to &#x60;asc&#x60;.", alias="order"),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> ChatCompletionList:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().list_chat_completions(model, metadata, after, limit, order)


@router.post(
    "/chat/completions/{completion_id}",
    responses={
        200: {"model": CreateChatCompletionResponse, "description": "A chat completion"},
    },
    tags=["Chat"],
    summary="Modify a stored chat completion. Only Chat Completions that have been created with the &#x60;store&#x60; parameter set to &#x60;true&#x60; can be modified. Currently, the only supported modification is to update the &#x60;metadata&#x60; field. ",
    response_model_by_alias=True,
)
async def update_chat_completion(
    completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to update.")] = Path(..., description="The ID of the chat completion to update."),
    update_chat_completion_request: UpdateChatCompletionRequest = Body(None, description=""),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> CreateChatCompletionResponse:
    if not BaseChatApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseChatApi.subclasses[0]().update_chat_completion(completion_id, update_chat_completion_request)
