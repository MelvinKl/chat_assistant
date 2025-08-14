import abc

from assistant.interfaces.knowledge import Knowledge


class KnowledgeDB(abc.ABC):

    @abc.abstractmethod
    async def aretrieve_knowledge(self, query: str) -> list[Knowledge]:
        """
        Retrieve knowledge from the DB base on the query.

        Parameters
        ----------
        query: str
            The basis of knowledge retrieval.

        Returns
        -------
        list[Knowledge]
            List of retrieved Knowledge.
        """

    @abc.abstractmethod
    async def aupdate_knowledge(self, conversation: list[str]) -> None:
        """
        Checks if the retrieved knowledge is still correct and updates it accordingly.
        Will also create new knowledge if required.

        Parameters
        ----------
        conversation: dict
            The conversation to retrieve knowledge from.
        """

    @abc.abstractmethod
    async def adelete_outdated_knowledge(self) -> None:
        """
        Checks the saved knowledge for oudated information and delete it.
        """
