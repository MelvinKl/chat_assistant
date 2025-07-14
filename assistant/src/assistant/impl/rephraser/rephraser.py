import asyncio
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

Input = dict
Output = str


class Rephraser(Runnable[Input, Output]):
    def __init__(self, llm: BaseChatModel, system_prompt, user_prompt):
        self._llm = llm
        self._prompt_template = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])

    async def ainvoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        return (await self._llm.ainvoke(self._prompt_template.invoke(state), config, **kwargs)).content

    def invoke(self, state: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        return asyncio.run(self.ainvoke(state, config, **kwargs))
