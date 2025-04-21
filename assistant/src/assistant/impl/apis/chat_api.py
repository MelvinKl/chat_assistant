from http.client import HTTPException
import time
from assistant.impl.graph.chat_graph import ChatGraph
from assistant.models.chat_completion_request_assistant_message import ChatCompletionRequestAssistantMessage
from assistant.models.chat_completion_request_developer_message import ChatCompletionRequestDeveloperMessage
from assistant.models.chat_completion_request_function_message import ChatCompletionRequestFunctionMessage
from assistant.models.chat_completion_request_system_message import ChatCompletionRequestSystemMessage
from assistant.models.chat_completion_request_tool_message import ChatCompletionRequestToolMessage
from assistant.models.chat_completion_request_user_message import ChatCompletionRequestUserMessage
import inject
from pydantic import Field, StrictInt, StrictStr, field_validator
from typing import Dict, Optional
from typing_extensions import Annotated
from assistant.models.chat_completion_deleted import ChatCompletionDeleted
from assistant.models.chat_completion_list import ChatCompletionList
from assistant.models.chat_completion_message_list import ChatCompletionMessageList
from assistant.models.create_chat_completion_request import CreateChatCompletionRequest
from assistant.models.create_chat_completion_response import CreateChatCompletionResponse
from assistant.models.update_chat_completion_request import UpdateChatCompletionRequest
from assistant.apis.chat_api_base import BaseChatApi

class ChatApi(BaseChatApi):

    @inject.autoparams("chat_graph")
    async def create_chat_completion(
        self,
        create_chat_completion_request: CreateChatCompletionRequest,
        chat_graph: ChatGraph,
    ) -> CreateChatCompletionResponse:
        history = []

        for message in create_chat_completion_request.messages:
            match message.actual_instance:
                case ChatCompletionRequestDeveloperMessage() as message:
                    history.append((message.role, message.content))
                case ChatCompletionRequestSystemMessage()as message:
                    history.append((message.role, message.content))
                case ChatCompletionRequestUserMessage() as message:
                    history.append((message.role, message.content))
                case ChatCompletionRequestAssistantMessage()as message:
                    history.append((message.role, message.content))
                case ChatCompletionRequestToolMessage()as message:
                    history.append((message.role, message.content))
                case ChatCompletionRequestFunctionMessage() as message:
                    history.append((message.role, message.content))
                case message:
                    raise HTTPException(status_code=422, detail=f"Received unknown message of type {type(message)}")
        
        result_message = await chat_graph.ainvoke(history)

        result = CreateChatCompletionResponse(
            id="create_chat_completion_request.id",
            choices=[result_message],
            created=int(time.time()),
            model=create_chat_completion_request.model,
            object="chat.completion",
        )
        return result



    async def delete_chat_completion(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to delete.")],
    ) -> ChatCompletionDeleted:
        raise HTTPException(status_code=500, detail="Not implemented")


    async def get_chat_completion(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to retrieve.")],
    ) -> CreateChatCompletionResponse:
        raise HTTPException(status_code=500, detail="Not implemented")


    async def get_chat_completion_messages(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to retrieve messages from.")],
        after: Annotated[Optional[StrictStr], Field(description="Identifier for the last message from the previous pagination request.")],
        limit: Annotated[Optional[StrictInt], Field(description="Number of messages to retrieve.")],
        order: Annotated[Optional[StrictStr], Field(description="Sort order for messages by timestamp. Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.")],
    ) -> ChatCompletionMessageList:
        raise HTTPException(status_code=500, detail="Not implemented")


    async def list_chat_completions(
        self,
        model: Annotated[Optional[StrictStr], Field(description="The model used to generate the Chat Completions.")],
        metadata: Annotated[Optional[Dict[str, StrictStr]], Field(description="A list of metadata keys to filter the Chat Completions by. Example:  `metadata[key1]=value1&metadata[key2]=value2` ")],
        after: Annotated[Optional[StrictStr], Field(description="Identifier for the last chat completion from the previous pagination request.")],
        limit: Annotated[Optional[StrictInt], Field(description="Number of Chat Completions to retrieve.")],
        order: Annotated[Optional[StrictStr], Field(description="Sort order for Chat Completions by timestamp. Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.")],
    ) -> ChatCompletionList:
        raise HTTPException(status_code=500, detail="Not implemented")


    async def update_chat_completion(
        self,
        completion_id: Annotated[StrictStr, Field(description="The ID of the chat completion to update.")],
        update_chat_completion_request: UpdateChatCompletionRequest,
    ) -> CreateChatCompletionResponse:
        raise HTTPException(status_code=500, detail="Not implemented")
