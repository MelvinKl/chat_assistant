from abc import ABC, abstractmethod


class ActEndpoint(ABC):

    @abstractmethod
    async def aact(self, request)->str:
        ...
