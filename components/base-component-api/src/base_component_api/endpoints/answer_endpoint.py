from abc import ABC, abstractmethod

from base_component_api.models.chat_response import ChatResponse


class AnswerEndpoint(ABC):

    @property
    @abstractmethod    
    def available(self) -> bool: ...

    @abstractmethod
    async def aanswer_question(self, question) -> ChatResponse: ...
