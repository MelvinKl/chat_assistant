from base_component_api.endpoints.assist_endpoint import AssistEndpoint
from base_component_api.models.chat_response import ChatResponse


class DefaultAnswerEndpoint(AssistEndpoint):

    async def aassist(self, query: str) -> ChatResponse:
        raise NotImplementedError()
