from abc import ABC, abstractmethod

from base_component_api.models.chat_response import ChatResponse


class AnswerEndpoint(ABC):

    @abstractmethod
    async def aanswer_question(self, question)->ChatResponse:
        ...
