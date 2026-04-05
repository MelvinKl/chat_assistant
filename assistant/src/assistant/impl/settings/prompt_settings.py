from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PromptSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_PROMPTS_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    rephrase_question_system_prompt: str = Field(default="")
    rephrase_question_user_prompt: str = Field(default="")

    rephrase_answer_system_prompt: str = Field(default="")
    rephrase_answer_user_prompt: str = Field(default="")

