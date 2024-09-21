from abc import ABC, abstractmethod

from langchain_core.documents import Document


class VectorDatabase(ABC):

    @abstractmethod
    def upload_documents(self, documents:list[Document])->None:
        ...

    @abstractmethod
    def search(self, query:str)->list[Document]:
        ...

    @property
    @abstractmethod    
    def retriever(self):
        ...