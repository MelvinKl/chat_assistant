from http.client import HTTPException
import time
from assistant.impl.graph.chat_graph import ChatGraph
from assistant.models.chat_completion_request import ChatCompletionRequest
from assistant.models.chat_completion_request_assistant_message import ChatCompletionRequestAssistantMessage
from assistant.models.chat_completion_request_developer_message import ChatCompletionRequestDeveloperMessage
from assistant.models.chat_completion_request_function_message import ChatCompletionRequestFunctionMessage
from assistant.models.chat_completion_request_system_message import ChatCompletionRequestSystemMessage
from assistant.models.chat_completion_request_tool_message import ChatCompletionRequestToolMessage
from assistant.models.chat_completion_request_user_message import ChatCompletionRequestUserMessage
from assistant.models.chat_completion_response import ChatCompletionResponse
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
    async def chat_completions(
        self,
        chat_completion_request: ChatCompletionRequest,
        chat_graph: ChatGraph,
    ) -> ChatCompletionResponse:        
        history = []

        for message in chat_completion_request.messages:
            history.append((message.role, message.content))
        
        result_message = await chat_graph.ainvoke(history)

        result = ChatCompletionResponse(
            id="create_chat_completion_request.id",
            choices=[result_message],
            created=int(time.time()),
            model=chat_completion_request.model,
            object="chat.completion",
        )
        return result