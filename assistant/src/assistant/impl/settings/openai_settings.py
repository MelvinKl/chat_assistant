from pydantic import Field
from pydantic_settings import BaseSettings


class OpenAISetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_OPENAI_"

    api_key: str = Field(default="sk-...")
    embedder: str = Field(default="text-embedding-3-small")
    model: str = Field(default="gpt-4o")
    base_url: str = Field(default="https://api.openai.com/v1")
