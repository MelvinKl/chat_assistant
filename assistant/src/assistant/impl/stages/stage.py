from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from assistant.impl.settings.system_one_settings import SystemOneSettings

Input = dict
Output = str


class Stage(Runnable[Input, Output]):
    """A question answering stage: an LLM call carrying the stage's own system prompt.

    The preprocessing stage runs on the question and the postprocessing
    stage on the returned answer. Each stage receives the tools of the MCP
    servers available to it and can run on an optional SystemOne model that
    limits the tools available to the stage LLM; a stage without a
    configured SystemOne model runs on the main LLM.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        user_prompt: str,
        tools: Optional[list[BaseTool]] = None,
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
        system_one: SystemOneSettings | None
            The SystemOne model the stage may run on; a configured (non-empty)
            model limits the tools available to the stage LLM. Defaults to None
        """
        self._llm = llm
        self._tools = list(tools) if tools else []
        self._system_one = system_one if system_one is not None and system_one.model else None
        self._prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])

    def create_llm(self) -> Runnable:
        """
        Create the LLM the stage runs on.

        A stage with a configured SystemOne model runs its LLM on that model,
        with the tools available to the stage LLM limited to the tools of the
        stage's available MCP servers; a stage without one runs on the main
        LLM.

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
        else:
            llm = self._llm
        if self._tools:
            llm = llm.bind_tools(self._tools)
        return llm

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
