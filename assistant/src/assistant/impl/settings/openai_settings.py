from pydantic import Field
from pydantic_settings import BaseSettings


class OpenAISetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_OPENAI_"

    # temperature: float = Field(0.7)
    api_key: str = Field()
    model: str = Field("Meta-Llama-3.1-8B-Instruct")
    base_url: str = Field("https://api.arliai.com/v1")
