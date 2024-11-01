import inject
from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.models.chat_response import ChatResponse
from base_library.impl.mapper.document_mapper import DocumentMapper
from base_library.vector_database.vector_database import VectorDatabase
from impl.prompts.answer_prompt import PROMPT
from langchain.chains import LLMChain
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate


class RagAnswerEndpoint(AnswerEndpoint):

    @property
    def available(self) -> bool:
        return True

    @inject.autoparams()
    def __init__(self, vector_database: VectorDatabase, llm:LLM):
        self._vector_database = vector_database
        self._llm = llm
        prompt_template = PromptTemplate.from_template(PROMPT)
        self._chain = prompt_template | llm

    async def aanswer_question(self, question:str) -> ChatResponse:
        search_result = self._vector_database.search(question)
        sources = [DocumentMapper.map_to_source_document(x) for x in search_result]

        answer = await self._chain.ainvoke(
            {"question": question, "context": "\n\n".join(x.page_content for x in search_result)}
        )
        return ChatResponse(sources=sources, answer=answer)
