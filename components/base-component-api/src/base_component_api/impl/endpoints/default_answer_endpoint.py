from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.models.chat_response import ChatResponse


class DefaultAnswerEndpoint(AnswerEndpoint):

    @property
    def available(self) -> bool:
        return False

    async def aanswer_question(self, question: str) -> ChatResponse:
        raise NotImplementedError()
