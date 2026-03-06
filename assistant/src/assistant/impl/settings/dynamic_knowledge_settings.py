from pydantic import Field
from pydantic_settings import BaseSettings


class DynamicKnowledgeSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_DYNAMIC_KNOWLEDGE_"

    enabled: bool = Field(default=False)
    collection_name: str = Field(default="")
    db_host: str = Field(default="localhost")
    max_items: int = Field(default=25)
    score_threshold: float = Field(default=0.25)
    system_prompt: str = Field(default="")
    user_prompt: str = Field(default="")
