from pydantic import Field
from pydantic_settings import BaseSettings


class DynamicKnowledgeSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_DYNAMIC_KNOWLEDGE_"

    enabled: bool = Field(default=False)
    collection_name: str = Field(default="knowledge")
    db_host: str = Field(default="http://localhost:6333")
    max_items: int = Field(default=25)
    score_threshold: float = Field(default=0.25)
    system_prompt: str = Field(default="system_prompt")
    user_prompt: str = Field(default="user_prompt")
