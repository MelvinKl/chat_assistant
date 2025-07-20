from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage

from langchain_core.outputs import ChatGeneration, ChatResult



# ------------------------------------------------------------
# Dummy / fake LLM helpers
# ------------------------------------------------------------


class FakeChatModel(BaseChatModel):
    """Stubbed LangChain LLM used in these tests."""

    answer:str=""
    kwargs_history:list[dict]=[]

    def __init__(self, answer: str, **kwargs):
        super().__init__(**kwargs)
        self.answer = answer
        self.kwargs_history: list[dict] = []  # store all captured kwargs

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.kwargs_history.append(kwargs)
        gen = ChatGeneration(message=AIMessage(content=self.answer))
        return ChatResult(generations=[gen])

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        return self._generate(messages=messages, stop=stop, run_manager=run_manager, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "fake-chat-model-for-testing"
