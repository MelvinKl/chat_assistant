from pydantic import Field
from pydantic_settings import BaseSettings


class OpenAISetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_OPENAI_"

    api_key: str = Field()
    embedder: str = Field()
    model: str = Field()
    base_url: str = Field()
