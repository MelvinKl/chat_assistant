from base_component_api.models.key_value import KeyValue
from langchain_core.documents import Document

from base_component_api.models.source_document import SourceDocument


class DocumentMapper:

    @staticmethod
    def map_to_source_document(document:Document)->SourceDocument:
        return SourceDocument(
            page_content=document.page_content,
            metadata = [KeyValue(name=key, value=str(value)) for key,value in document.metadata.items()]
        )