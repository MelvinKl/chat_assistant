# coding: utf-8

from typing import ClassVar

from assistant.models.chat_completion_request import ChatCompletionRequest
from assistant.models.chat_completion_response import ChatCompletionResponse


class BaseChatApi:
    subclasses: ClassVar[tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseChatApi.subclasses = BaseChatApi.subclasses + (cls,)

    async def chat_completions(
        self,
        chat_completion_request: ChatCompletionRequest,
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
