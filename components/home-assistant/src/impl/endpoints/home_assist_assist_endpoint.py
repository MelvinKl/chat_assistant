from impl.tools import create_tools
import inject
from base_component_api.endpoints.assist_endpoint import AssistEndpoint
from base_component_api.models.chat_response import ChatResponse
from base_library.impl.mapper.document_mapper import DocumentMapper
from base_library.vector_database.vector_database import VectorDatabase
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate

from impl.prompts.answer_prompt import PROMPT


class HomeAssistAssistEndpoint(AssistEndpoint):

    @property
    def available(self) -> bool:
        return True

    @inject.autoparams()
    def __init__(self, llm: LLM):
        self._tools = create_tools()
        self._llm = llm
        prompt_template = PromptTemplate.from_template(PROMPT)
        self._chain = prompt_template | llm

    async def aassist(self, question: str) -> ChatResponse:
        print(self._tools[0].invoke(""))
        return ChatResponse(sources=[], answer="answer")
