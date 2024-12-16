from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint

from tracely import trace_event
from fastapi import File, UploadFile


class UploadDocumentEndpoint(UploadDocumentEndpoint):

    @trace_event
    def upload_documents(self, file: UploadFile = File(...)) -> None:
        raise NotImplementedError()
