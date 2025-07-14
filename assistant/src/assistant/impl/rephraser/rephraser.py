import asyncio
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

Input = dict
Output = str


class Rephraser(Runnable[Input, Output]):
    """Langchain Runnable used for rephrasing. Allows for special instructions using a system prompt."""

    def __init__(self, llm: BaseChatModel, system_prompt: str, user_prompt: str):
        """
        Constructor for the Rephraser

        Parameters
        ----------
        llm : BaseChatModel
            The llm instance to use for rephrasing.
        system_prompt: str
            Prompt template for the system prompt.
        user_prompt: str
            Prompt template for the user prompt.
        """
        self._llm = llm
        self._prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])

    async def ainvoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Processes a rephrasing request.

        Parameters
        ----------
        state : dict
            The current state. Need to contain information required for rephrasing.
        config: RunnableConfig
            configuration for the llm. Defaults to None
        kwargs: Any
            Additional configuration parameters for the llm call.

        Returns
        -------
        str
            The rephrased input
        """
        return (await self._llm.ainvoke(self._prompt_template.invoke(state), config, **kwargs)).content

    def invoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        """
        Processes a rephrasing request.

        Parameters
        ----------
        state : dict
            The current state. Need to contain information required for rephrasing.
        config: RunnableConfig
            configuration for the llm. Defaults to None
        kwargs: Any
            Additional configuration parameters for the llm call.

        Returns
        -------
        str
            The rephrased input
        """
        return asyncio.run(self.ainvoke(state, config, **kwargs))
