from typing import Optional, Type
from impl.settings.home_assistant_settings import HomeAssistantSetttings
import inject
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field
from homeassistant_api import Client
from homeassistant_api.models import Group

@inject.autoparams()
def create_tools(settings:HomeAssistantSetttings)->list[BaseTool]:
    tools = []
    client = Client(settings.url, settings.apikey)
    tools.append(HomeAssistantStateTool(client=client))
    return tools


class ComponentInput(BaseModel):
    query: str = Field(description="is unused")

class HomeAssistantStateTool(BaseTool):
    name: str = "state-tool"
    description: str = "Lists all entitites and their current state."
    client: Client
    args_schema: Type[BaseModel] = ComponentInput
    return_direct: bool = True

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict[str, Group]:
        """Use the tool."""
        return self.client.get_entities()

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> dict[str, Group]:
        """Use the tool asynchronously."""
        return await self.client.async_get_entities()
