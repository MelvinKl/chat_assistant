from pydantic import Field
from pydantic_settings import BaseSettings


class PromptSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_PROMPTS_"

    rephrase_question_prompt: str = Field(
        """
            Rephrase the question so it contains all the relevant information from the history required to answer the question.
                                                       
            Question: {question}
            History: {history}
        """
    )

    rephrase_answer_prompt: str = Field(
        """
            You are James, a butler of the aristocracy. You were told to do {question}. You determined that the correct answer is {raw_answer}.
            Rephrase this answer. Answer in the following language: {question_language}.
        """
    )
