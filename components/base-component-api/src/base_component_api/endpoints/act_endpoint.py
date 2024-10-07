from abc import ABC, abstractmethod


class ActEndpoint(ABC):

    @abstractmethod
    @property
    def available(self)->bool:
        ...

    @abstractmethod
    async def aact(self, request)->str:
        ...
