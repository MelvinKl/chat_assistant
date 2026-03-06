from pydantic import Field
from pydantic_settings import BaseSettings


class OpenAISetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_OPENAI_"

    api_key: str = Field(default="")
    embedder: str = Field(default="")
    model: str = Field(default="")
    base_url: str = Field(default="")
