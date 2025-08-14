import uuid


from langchain_core.documents import Document

from assistant.interfaces.knowledge import Knowledge


class KnowledgeMapper:
    @staticmethod
    def to_document(knowledge: Knowledge) -> Document:
        if not knowledge.uuid:
            knowledge.uuid = uuid.uuid4()
        return Document(
            page_content=knowledge.information,
            metadata={
                "id": knowledge.uuid,
                "expiration_date": knowledge.expiration_date,
            },
            id=knowledge.uuid,
        )

    @staticmethod
    def from_document(document: Document) -> Knowledge:
        return Knowledge(
            expiration_date=document.metadata["expiration_date"],
            information=document.page_content,
            uuid=document.metadata["id"],
        )
