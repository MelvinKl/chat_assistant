from base_component_api.endpoints.upload_document_endpoint import \
    UploadDocumentEndpoint
from fastapi import File, UploadFile


class UploadDocumentEndpoint(UploadDocumentEndpoint):

    def upload_documents(self, file: UploadFile = File(...)) -> None:
        raise NotImplementedError()
