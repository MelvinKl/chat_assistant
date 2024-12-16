from fastapi import File, UploadFile

from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint


class UploadDocumentEndpoint(UploadDocumentEndpoint):

    def upload_documents(self, file: UploadFile = File(...)) -> None:
        raise NotImplementedError()
