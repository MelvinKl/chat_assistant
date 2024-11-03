from abc import ABC, abstractmethod

from base_component_api.models.description import Description


class GetDescriptionEndpoint(ABC):

    @abstractmethod
    def get_description(self) -> Description: ...
