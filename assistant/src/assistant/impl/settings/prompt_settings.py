from pydantic import Field
from pydantic_settings import BaseSettings


class PromptSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_PROMPTS_"

    rephrase_question_system_prompt: str = Field()
    rephrase_question_user_prompt: str = Field()

    rephrase_answer_system_prompt: str = Field()
    rephrase_answer_user_prompt: str = Field()
