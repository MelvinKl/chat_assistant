from typing import Any

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_core.documents import Document

from base_library.document_extractor.document_type import DocumentType
from base_library.document_extractor.extractor import Extractor


class PDFExtractor(Extractor):

    @property
    def supported_types(self) -> list[DocumentType]:
        return [DocumentType.PDF]

    def extract(self, content: Any) -> list[Document]:
        loader = PDFPlumberLoader(content)
        return loader.load()
