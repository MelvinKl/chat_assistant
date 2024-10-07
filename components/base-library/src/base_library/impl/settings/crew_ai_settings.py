from pydantic import Field
from pydantic_settings import BaseSettings


class OpenAISetttings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_CREWAI_"

    embedder_provider: str = Field("huggingface")
    embedder_model: str = Field("mixedbread-ai/mxbai-embed-large-v1")
