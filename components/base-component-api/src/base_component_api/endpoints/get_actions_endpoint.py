from abc import ABC, abstractmethod


class GetActionsEndpoint(ABC):

    @abstractmethod
    def get_actions(self)->dict:
        ...
