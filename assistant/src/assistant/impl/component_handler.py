from typing import Optional, Type

import inject
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from assistant.component_api.api.component_api import ComponentApi
from assistant.component_api.api_client import ApiClient
from assistant.component_api.configuration import Configuration
from assistant.impl.settings.component_settings import ComponentSetttings


class ComponentHandler:

    @inject.autoparams()
    def __init__(self, llm: BaseChatModel, component_settings: ComponentSetttings) -> None:
        self._settings = component_settings
        self._tools = self._create_tools()
        self._agent = llm.bind_tools(self._tools)
        self._chain = create_react_agent(llm, tools=self._tools, prompt="You are a helpful assistant")

    async def aanswer_question(self, question: str) -> str:
        response = await self._chain.ainvoke({"messages": [("user", question)]})
        return response["messages"][-1].content

    def _create_tools(self) -> list[BaseTool]:
        tools = []
        for component in self._settings.apis:
            client = ComponentApi(ApiClient(configuration=Configuration(host=component)))
            description_response = client.get_description()
            description = description_response.description
            name = description_response.name
            tools.append(ComponentTool(client=client, name=name, description=description))
        return tools


class ComponentInput(BaseModel):
    query: str = Field(description="should be a search query")


class ComponentTool(BaseTool):

    name: str
    description: str
    client: ComponentApi
    args_schema: Type[BaseModel] = ComponentInput
    return_direct: bool = True

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        return self.client.assist(query).answer

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return self._run(query, run_manager)
