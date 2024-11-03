import inject
from fastapi import UploadFile

from base_component_api.apis.component_api_base import BaseComponentApi
from base_component_api.endpoints.assist_endpoint import AssistEndpoint
from base_component_api.endpoints.get_description_endpoint import GetDescriptionEndpoint
from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint
from base_component_api.models.chat_response import ChatResponse
from base_component_api.models.key_value import KeyValue


class ComponentApiImplementation(BaseComponentApi):

    @inject.autoparams("assist_endpoint")
    async def assist(
        self,
        body: str,
        assist_endpoint: AssistEndpoint,
    ) -> ChatResponse:
        return await assist_endpoint.aassist(body)

    @inject.autoparams("get_descriptions_endpoint")
    async def get_available_actions(
        self,
        get_descriptions_endpoint: GetDescriptionEndpoint,
    ) -> list[KeyValue]:
        available_actions = get_descriptions_endpoint.get_description()
        return [KeyValue(Name=str(key), Value=str(value)) for key, value in available_actions.items()]

    @inject.autoparams("upload_document_endpoint")
    async def upload_document(
        self,
        file: UploadFile,
        upload_document_endpoint: UploadDocumentEndpoint,
    ) -> None:
        upload_document_endpoint.upload_documents(file)
