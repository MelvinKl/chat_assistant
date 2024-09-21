from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.models.chat_response import ChatResponse


class DefaultAnswerEndpoint(AnswerEndpoint):
    
    async def aanswer_question(self, question)->ChatResponse:
        raise NotImplementedError()
