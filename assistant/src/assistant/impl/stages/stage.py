import json
import logging
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from assistant.impl.settings.system_one_settings import SystemOneSettings

logger = logging.getLogger(__name__)

Input = dict
Output = str


FILTER_MCP_SERVERS_PROMPT = (
    "You are the SystemOne model of a question answering stage of a chat assistant. "
    "The stage's system prompt is:\n{system_prompt}\n"
    "The MCP servers available to the stage are: {servers}.\n"
    "Decide which of the available MCP servers the stage needs for its task. "
    "Answer with a JSON array of the names of the servers to keep, or an empty array if it needs none."
)


class Stage(Runnable[Input, Output]):
    """A question answering stage: an LLM call carrying the stage's own system prompt.

    The preprocessing stage runs on the question and the postprocessing
    stage on the returned answer. Each stage receives the tools of the MCP
    servers available to it and can run on an optional SystemOne model that
    limits the tools available to the stage LLM and filters the MCP servers
    available to the stage when the stage LLM is created; a stage without a
    configured SystemOne model runs on the main LLM.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        user_prompt: str,
        tools: Optional[list[BaseTool]] = None,
        mcp_servers: Optional[dict[str, list[BaseTool]]] = None,
        system_one: Optional[SystemOneSettings] = None,
    ):
        """
        Constructor for the Stage

        Parameters
        ----------
        llm : BaseChatModel
            The main LLM the stage runs on when no SystemOne model is configured.
        system_prompt: str
            The system prompt of the stage; the stage LLM call carries it.
        user_prompt: str
            Prompt template for the user prompt, rendered from the state.
        tools: list[BaseTool] | None
            The tools of the MCP servers available to the stage. Defaults to None
        mcp_servers: dict[str, list[BaseTool]] | None
            The MCP servers available to the stage, keyed by the server name:
            the loaded tools of each server. When a SystemOne model is
            configured, the stage LLM is created with the tools of the servers
            the model keeps. Defaults to None
        system_one: SystemOneSettings | None
            The SystemOne model the stage may run on; a configured (non-empty)
            model limits the tools available to the stage LLM and filters the
            MCP servers available to the stage. Defaults to None
        """
        self._llm = llm
        self._system_prompt = system_prompt
        self._mcp_servers = dict(mcp_servers) if mcp_servers else {}
        if tools:
            self._tools = list(tools)
        elif self._mcp_servers:
            self._tools = [tool for server_tools in self._mcp_servers.values() for tool in server_tools]
        else:
            self._tools = []
        self._system_one = system_one if system_one is not None and system_one.model else None
        self._prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])

    def create_llm(self) -> Runnable:
        """
        Create the LLM the stage runs on.

        A stage with a configured SystemOne model runs its LLM on that model,
        with the tools available to the stage LLM limited to the tools of the
        stage's available MCP servers; the MCP servers available to the stage
        are filtered by the SystemOne model and only the servers the model
        keeps contribute their tools to the stage LLM. A stage without one
        runs on the main LLM.

        Returns
        -------
        Runnable
            The stage LLM, bound to the tools of the stage's available MCP
            servers when the stage carries any
        """
        if self._system_one is not None:
            llm = ChatOpenAI(
                model=self._system_one.model,
                base_url=self._system_one.base_url,
                api_key=self._system_one.api_key,
            )
            if self._mcp_servers:
                kept = self._filter_mcp_servers(llm)
                if kept is None:
                    tools = self._tools
                else:
                    tools = [tool for name in kept for tool in self._mcp_servers.get(name, [])]
            else:
                tools = self._tools
        else:
            llm = self._llm
            tools = self._tools
        if tools:
            llm = llm.bind_tools(tools)
        return llm

    def _filter_mcp_servers(self, system_one_llm: BaseChatModel) -> Optional[list[str]]:
        """Filter the MCP servers available to the stage with the SystemOne model.

        The model is consulted with the stage's system prompt and the names of
        the stage's available MCP servers and answers with the names of the
        servers the stage keeps.

        Parameters
        ----------
        system_one_llm : BaseChatModel
            The SystemOne model the stage runs on.

        Returns
        -------
        list[str] | None
            The names of the servers the model keeps (unknown names are
            dropped); None when the model's answer cannot be read as a server
            selection — then the stage keeps all of its available MCP servers
        """
        prompt = FILTER_MCP_SERVERS_PROMPT.format(
            system_prompt=self._system_prompt,
            servers=", ".join(self._mcp_servers),
        )
        try:
            response = system_one_llm.invoke(prompt)
        except Exception as e:
            logger.error("The SystemOne model failed to filter the MCP servers of the stage: %s", e)
            return None
        try:
            selection = json.loads(response.content)
        except (TypeError, ValueError) as e:
            logger.warning(
                "The SystemOne model's answer %r is not a server selection; keeping all MCP servers of the stage: %s",
                response.content,
                e,
            )
            return None
        if not isinstance(selection, list) or not all(isinstance(name, str) for name in selection):
            logger.warning(
                "The SystemOne model's answer %r is not a list of server names; keeping all MCP servers of the stage",
                response.content,
            )
            return None
        return [name for name in selection if name in self._mcp_servers]

    async def ainvoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Runs the stage: invokes the stage LLM with the stage's system prompt
        and the user content rendered from the state.

        Parameters
        ----------
        state : dict
            The current state. Need to contain the content the stage runs on.
        config: RunnableConfig
            configuration for the llm. Defaults to None
        kwargs: Any
            Additional configuration parameters for the llm call.

        Returns
        -------
        str
            The answer the stage LLM produced
        """
        prompt = self._prompt_template.invoke(state)
        answer = await self.create_llm().ainvoke(prompt, config, **kwargs)
        return answer.content

    def invoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Runs the stage (sync twin of ainvoke).

        Parameters
        ----------
        state : dict
            The current state. Need to contain the content the stage runs on.
        config: RunnableConfig
            configuration for the llm. Defaults to None
        kwargs: Any
            Additional configuration parameters for the llm call.

        Returns
        -------
        str
            The answer the stage LLM produced
        """
        prompt = self._prompt_template.invoke(state)
        answer = self.create_llm().invoke(prompt, config, **kwargs)
        return answer.content
