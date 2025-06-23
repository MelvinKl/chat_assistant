# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from typing import Any
from assistant.models.chat_completion_request import ChatCompletionRequest
from assistant.models.chat_completion_response import ChatCompletionResponse


class BaseChatApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseChatApi.subclasses = BaseChatApi.subclasses + (cls,)

    async def chat_completions(
        self,
        chat_completion_request: ChatCompletionRequest,
    ) -> ChatCompletionResponse: ...
