from langchain_core.documents import Document

from assistant.interfaces.knowledge import Knowledge


class KnowledgeMapper:
    def to_document(self, knowledge: Knowledge) -> Document:
        return Document(
            page_content=knowledge.information,
            metadata={
                "id": knowledge.uuid,
                "expiration_date": knowledge.expiration_date,
            },
            id=str(knowledge.uuid),
        )

    def from_document(self, document: Document) -> Knowledge:
        metadata = document.metadata
        return Knowledge(
            information=document.page_content,
            uuid=metadata.get("id"),
            expiration_date=metadata.get("expiration_date"),
        )
