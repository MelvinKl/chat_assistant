from abc import ABC, abstractmethod

from base_component_api.models.chat_response import ChatResponse


class AssistEndpoint(ABC):

    @abstractmethod
    async def aassist(self, query: str) -> ChatResponse: ...
