import inject
from pydantic import StrictStr

from assistant.apis.assistant_api_base import BaseAssistantApi
from assistant.impl.component_handler import ComponentHandler


class AssistantAPI(BaseAssistantApi):

    @inject.autoparams("component_handler")
    async def assist(
        self,
        body: StrictStr,
        component_handler: ComponentHandler,
    ) -> str:
        # TODO: handle personality of assistant, language, etc. This should be done using langgraph
        return await component_handler.aanswer_question(body)
