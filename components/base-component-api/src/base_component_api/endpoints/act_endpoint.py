from abc import ABC, abstractmethod


class ActEndpoint(ABC):

    @property
    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    async def aact(self, request) -> str: ...
