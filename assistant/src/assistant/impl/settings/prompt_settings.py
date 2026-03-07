from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = Path(__file__).parent.parent.parent.parent.parent / ".env"


class PromptSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_PROMPTS_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    rephrase_question_system_prompt: str = Field()
    rephrase_question_user_prompt: str = Field()

    rephrase_answer_system_prompt: str = Field()
    rephrase_answer_user_prompt: str = Field()
