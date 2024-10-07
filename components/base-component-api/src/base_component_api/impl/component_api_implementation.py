from fastapi import Depends, File, UploadFile
from dependency_injector.wiring import Provide, inject

from base_component_api.apis.component_api_base import BaseComponentApi
from base_component_api.dependency_container import DependencyContainer
from base_component_api.endpoints.act_endpoint import ActEndpoint
from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.endpoints.get_actions_endpoint import GetActionsEndpoint
from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint
from base_component_api.models.chat_response import ChatResponse
from base_component_api.models.key_value import KeyValue


class ComponentApiImplementation(BaseComponentApi):

    @inject
    async def act(
        self,
        body: str,
        act_endpoint: ActEndpoint = Depends(Provide[DependencyContainer.act_endpoint]),
    ) -> str:
        return await act_endpoint.aact(body)

    @inject
    async def answer_question(
        self,
        body: str,
        answer_endpoint: AnswerEndpoint = Depends(Provide[DependencyContainer.answer_endpoint]),
    ) -> ChatResponse:
        return await answer_endpoint.aanswer_question(body)

    @inject
    async def get_available_actions(
        self,
        get_actions_endpoint: GetActionsEndpoint = Depends(Provide[DependencyContainer.get_actions_endpoint]),
    ) -> list[KeyValue]:
        available_actions = get_actions_endpoint.get_actions()
        return [KeyValue(Name=key, Value=value) for key, value in available_actions.items()]

    @inject
    async def upload_document(
        self,
        file: UploadFile = File(...),
        upload_document_endpoint: UploadDocumentEndpoint = Depends(
            Provide[DependencyContainer.upload_document_endpoint]
        ),
    ) -> None:
        upload_document_endpoint.upload_documents(file)
