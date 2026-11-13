from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemOneSettings(BaseSettings):
    """The optional SystemOne model a question answering stage may run on.

    A stage configured with a SystemOne model (a non-empty ``model``) runs
    its LLM on that model, with the tools available to the stage LLM limited
    to the tools of the stage's available MCP servers; a stage without one
    runs on the main LLM.
    """

    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_SYSTEM_ONE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str = Field(default="")
    base_url: str = Field(default="")
    api_key: str = Field(default="")
