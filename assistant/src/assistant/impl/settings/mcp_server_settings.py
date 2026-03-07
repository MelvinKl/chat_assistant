import json

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServer(BaseModel):
    url: str = ""
    name: str
    command: str = ""
    args: list[str] = []
    env: str = ""
    transport: str
    headers: dict[str, str] | None = None


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SETTINGS_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    servers: list[MCPServer] = Field()


def load_mcp_settings_from_json(
    json_file_path="/config/mcp/SETTINGS_MCP_SERVERS",
) -> MCPSettings:
    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return MCPSettings(servers=[])

    cleaned_data = (
        {"servers": data["servers"]} if "servers" in data else {"servers": []}
    )
    return MCPSettings(**cleaned_data)
