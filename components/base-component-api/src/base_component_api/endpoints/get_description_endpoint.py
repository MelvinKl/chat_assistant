from abc import ABC, abstractmethod


class GetDescriptionEndpoint(ABC):

    @abstractmethod
    def get_description(self) -> dict: ...
