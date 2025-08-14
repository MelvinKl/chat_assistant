import inject
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from assistant.interfaces.knowledge import Knowledge


class KnowledgeCheckerModel(BaseModel):
    new_knowledge: list[Knowledge] = Field(
        description="List of knowledge that needs to be added. These new Knowledge pieces should not have an ID."
    )
    updated_knowledge: list[Knowledge] = Field(
        description="""List of existing knowledge elements that needs to be update.
        Ensure that the ID matches and the information is updated."""
    )
    outdated_knowledge: list[Knowledge] = Field(
        description="List of existing knowledge elements that should be deleted."
    )


class KnowledgeChecker:

    @inject.params(
        llm=BaseChatModel,
        prompt_template="dynamic_knowledge_prompt_template",
    )
    def __init__(self, llm: BaseChatModel, prompt_template: ChatPromptTemplate):
        self._prompt_template = prompt_template
        self._llm = llm.with_structured_output(KnowledgeCheckerModel)

    async def acheck_knowledge(
        self, conversation: dict, retrieved_knowledge: list[Knowledge]
    ) -> tuple[list[Knowledge], list[Knowledge], list[Knowledge]]:
        retrieved_knowledge_string = "\n".join(retrieved_knowledge)
        conversation_string = "\n".join([f"{key}:{value}" for key, value in conversation.items()])

        result = await self._llm.ainvoke(
            self._prompt_template.invoke(
                {"conversation": conversation_string, "retrieved_knowledge": retrieved_knowledge_string}
            )
        )

        return result.new_knowledge, result.updated_knowledge, result.outdated_knowledge
