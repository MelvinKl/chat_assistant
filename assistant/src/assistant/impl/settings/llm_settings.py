from pydantic import Field
from pydantic_settings import BaseSettings


class LLMSetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_LLM_"

    provider: str = Field("ollama")
