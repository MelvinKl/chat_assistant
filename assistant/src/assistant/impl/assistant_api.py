from pydantic import StrictStr
from assistant.apis.assistant_api_base import BaseAssistantApi


class AssistantAPI(BaseAssistantApi):
    async def assist(
        self,
        body: StrictStr,
    ) -> str:
        return body
