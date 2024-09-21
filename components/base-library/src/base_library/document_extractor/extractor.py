from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document

from base_library.document_extractor.document_type import DocumentType



class Extractor(ABC):

    @property
    @abstractmethod    
    def supported_types(self)->list[DocumentType]:
        ...

    @abstractmethod
    def extract(self, content:Any)->list[Document]:
        ...