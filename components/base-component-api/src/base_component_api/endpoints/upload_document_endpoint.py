from abc import ABC, abstractmethod

from fastapi import File, UploadFile


class UploadDocumentEndpoint(ABC):    

    @abstractmethod
    def upload_documents(self, file: UploadFile = File(...)) -> None:
        ...
