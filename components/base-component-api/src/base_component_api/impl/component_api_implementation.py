import inject
from fastapi import UploadFile

from base_component_api.apis.component_api_base import BaseComponentApi
from base_component_api.endpoints.act_endpoint import ActEndpoint
from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.endpoints.get_actions_endpoint import GetActionsEndpoint
from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint
from base_component_api.models.chat_response import ChatResponse
from base_component_api.models.key_value import KeyValue


class ComponentApiImplementation(BaseComponentApi):

    @inject.autoparams("act_endpoint")
    async def act(
        self,
        body: str,
        act_endpoint: ActEndpoint,
    ) -> str:
        return await act_endpoint.aact(body)

    @inject.autoparams("answer_endpoint")
    async def answer_question(
        self,
        body: str,
        answer_endpoint: AnswerEndpoint,
    ) -> ChatResponse:
        return await answer_endpoint.aanswer_question(body)

    @inject.autoparams("get_actions_endpoint")
    async def get_available_actions(
        self,
        get_actions_endpoint: GetActionsEndpoint,
    ) -> list[KeyValue]:
        available_actions = get_actions_endpoint.get_actions()
        return [KeyValue(Name=str(key), Value=str(value)) for key, value in available_actions.items()]

    @inject.autoparams("upload_document_endpoint")
    async def upload_document(
        self,
        file: UploadFile,
        upload_document_endpoint: UploadDocumentEndpoint,
    ) -> None:
        upload_document_endpoint.upload_documents(file)
