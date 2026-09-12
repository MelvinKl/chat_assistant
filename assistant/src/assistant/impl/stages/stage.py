"""Module for the Stage runnable."""

from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool

Input = dict
Output = str

MAX_TOOL_ITERATIONS = 5


class Stage(Runnable[Input, Output]):
    """
    Langchain Runnable for a question answering stage, e.g. preprocessing or postprocessing.

    A stage has its own system prompt and user prompt and can use the MCP
    servers (tools) that are assigned to it.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        user_prompt: str,
        tools: Optional[list[BaseTool]] = None,
    ):
        """
        Constructor for the Stage

        Parameters
        ----------
        llm : BaseChatModel
            The llm instance to use for the stage.
        system_prompt: str
            Prompt template for the system prompt.
        user_prompt: str
            Prompt template for the user prompt.
        tools: list[BaseTool] | None
            The MCP server tools that are available in this stage. Defaults to None.
        """
        self._llm = llm.bind_tools(tools) if tools else llm
        self._tools = {tool.name: tool for tool in (tools or [])}
        self._prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])

    def _tool_messages(self, message: BaseMessage) -> list[ToolMessage]:
        """Create a ToolMessage for every tool call of the given message."""
        tool_messages = []
        for tool_call in message.tool_calls:
            tool = self._tools.get(tool_call["name"])
            if tool is None:
                tool_messages.append(ToolMessage(content="Tool not found.", tool_call_id=tool_call["id"]))
            else:
                result = tool.invoke(tool_call["args"])
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        return tool_messages

    async def _atool_messages(self, message: BaseMessage) -> list[ToolMessage]:
        """Create a ToolMessage for every tool call of the given message (async)."""
        tool_messages = []
        for tool_call in message.tool_calls:
            tool = self._tools.get(tool_call["name"])
            if tool is None:
                tool_messages.append(ToolMessage(content="Tool not found.", tool_call_id=tool_call["id"]))
            else:
                result = await tool.ainvoke(tool_call["args"])
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        return tool_messages

    def invoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Processes a stage request.

        Parameters
        ----------
        state : dict
            The current state. Need to contain information required for the stage.
        config: RunnableConfig
            configuration for the llm. Defaults to None
        kwargs: Any
            Additional configuration parameters for the llm call.

        Returns
        -------
        str
            The result of the stage
        """
        messages: list[BaseMessage] = self._prompt_template.invoke(state).to_messages()
        message = self._llm.invoke(messages, config, **kwargs)
        for _ in range(MAX_TOOL_ITERATIONS):
            if not message.tool_calls:
                return message.content
            messages = messages + [message] + self._tool_messages(message)
            message = self._llm.invoke(messages, config, **kwargs)
        return message.content

    async def ainvoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Processes a stage request.

        Parameters
        ----------
        state : dict
            The current state. Need to contain information required for the stage.
        config: RunnableConfig
            configuration for the llm. Defaults to None
        kwargs: Any
            Additional configuration parameters for the llm call.

        Returns
        -------
        str
            The result of the stage
        """
        messages: list[BaseMessage] = self._prompt_template.invoke(state).to_messages()
        message = await self._llm.ainvoke(messages, config, **kwargs)
        for _ in range(MAX_TOOL_ITERATIONS):
            if not message.tool_calls:
                return message.content
            messages = messages + [message] + await self._atool_messages(message)
            message = await self._llm.ainvoke(messages, config, **kwargs)
        return message.content
