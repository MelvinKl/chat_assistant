import time
import uuid

import inject

from assistant.apis.chat_api_base import BaseChatApi
from assistant.impl.graph.chat_graph import ChatGraph
from assistant.models.chat_completion_choice import ChatCompletionChoice
from assistant.models.chat_completion_choice_message import ChatCompletionChoiceMessage
from assistant.models.chat_completion_request import ChatCompletionRequest
from assistant.models.chat_completion_response import ChatCompletionResponse
from assistant.models.chat_completion_usage import ChatCompletionUsage


class ChatApi(BaseChatApi):
    """Implementation of OpenAI compatible chat API for chat assistant."""

    @inject.autoparams("chat_graph")
    async def chat_completions(
        self,
        chat_completion_request: ChatCompletionRequest,
        chat_graph: ChatGraph,
    ) -> ChatCompletionResponse:
        """
        Processes a chat completion request and returns a chat completion response.

        Parameters
        ----------
        chat_completion_request : ChatCompletionRequest
            The request object containing the necessary information for the chat completion.

        Returns
        -------
        ChatCompletionResponse
            The response object containing the result of the chat completion process.
        """
        history = []

        for message in chat_completion_request.messages:
            history.append((message.role, message.content))

        result_message = await chat_graph.ainvoke(history)

        return ChatCompletionResponse(
            id=str(uuid.uuid4()),
            choices=[
                ChatCompletionChoice(
                    finish_reason="stop",
                    index=0,
                    message=ChatCompletionChoiceMessage(content=result_message, role="assistant"),
                )
            ],
            created=int(time.time()),
            model=chat_completion_request.model,
            object="chat.completion",
            usage=ChatCompletionUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )
