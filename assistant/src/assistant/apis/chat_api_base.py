# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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

class BaseChatApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseChatApi.subclasses = BaseChatApi.subclasses + (cls,)
    async def create_chat_completion(
        self,
        create_chat_completion_request: CreateChatCompletionRequest,
    ) -> CreateChatCompletionResponse:
        ...


    async def delete_chat_completion(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to delete.")],
    ) -> ChatCompletionDeleted:
        ...


    async def get_chat_completion(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to retrieve.")],
    ) -> CreateChatCompletionResponse:
        ...


    async def get_chat_completion_messages(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to retrieve messages from.")],
        after: Annotated[Optional[StrictStr], Field(description="Identifier for the last message from the previous pagination request.")],
        limit: Annotated[Optional[StrictInt], Field(description="Number of messages to retrieve.")],
        order: Annotated[Optional[StrictStr], Field(description="Sort order for messages by timestamp. Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.")],
    ) -> ChatCompletionMessageList:
        ...


    async def list_chat_completions(
        self,
        model: Annotated[Optional[StrictStr], Field(description="The model used to generate the Chat Completions.")],
        metadata: Annotated[Optional[Dict[str, StrictStr]], Field(description="A list of metadata keys to filter the Chat Completions by. Example:  `metadata[key1]=value1&metadata[key2]=value2` ")],
        after: Annotated[Optional[StrictStr], Field(description="Identifier for the last chat completion from the previous pagination request.")],
        limit: Annotated[Optional[StrictInt], Field(description="Number of Chat Completions to retrieve.")],
        order: Annotated[Optional[StrictStr], Field(description="Sort order for Chat Completions by timestamp. Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.")],
    ) -> ChatCompletionList:
        ...


    async def update_chat_completion(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to update.")],
        update_chat_completion_request: UpdateChatCompletionRequest,
    ) -> CreateChatCompletionResponse:
        ...
