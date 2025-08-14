from langchain_core.documents import Document

from assistant.interfaces.knowledge import Knowledge
from assistant.interfaces.knowledge_db import KnowledgeDB


class DummyKnowledgeDB(KnowledgeDB):

    async def aretrieve_knowledge(self, query: str) -> list[Knowledge]:
        return []

    async def aupdate_knowledge(self, conversation: list[str]) -> None:
        return

    async def adelete_outdated_knowledge(self) -> None:
        return

    async def _adelete_documents(self, document: Document) -> None:
        return

    async def _aupsert_documents(self, document: Document) -> None:
        return
