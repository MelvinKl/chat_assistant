from pydantic import BaseModel, Field
from assistant.component_api.api.component_api import ComponentApi
from assistant.component_api.api_client import ApiClient
from assistant.component_api.configuration import Configuration
from langchain.tools import BaseTool, StructuredTool, tool
from assistant.impl.settings.component_settings import ComponentSetttings
import inject
from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

class ComponentHandler:

    @inject.autoparams()
    def __init__(self, component_settings:ComponentSetttings)->None:
        self._settings = component_settings
        self._tools = self._create_tools()

    def _create_tools(self) -> list[BaseTool]:
        return [ComponentTool(ComponentApi(ApiClient(configuration=Configuration(host=component.url))),component.url) for component in self._settings.apis]


class ComponentInput(BaseModel):
    query: str = Field(description="should be a search query")


class ComponentTool(BaseTool):

    name = "Calculator"
    description = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = ComponentInput
    return_direct: bool = True

    def __init__(self, component_api_client:ComponentApi,url:str)->None:
        self._client = component_api_client
        self.name = url
        description = self._client.get_description()

    def _run(
        self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return self._client.assist(query)

    async def _arun(
        self,
        query:str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return self._run(query, run_manager)