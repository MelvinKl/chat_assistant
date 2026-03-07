import json
import os

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


def load_mcp_settings_from_json(json_file_path=None) -> MCPSettings:
    if json_file_path is None:
        json_file_path = os.environ.get(
            "MCP_SETTINGS_PATH", "/config/mcp/SETTINGS_MCP_SERVERS"
        )

    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"servers": []}

    cleaned_data = {"servers": data["servers"]} if "servers" in data else {}
    return MCPSettings(**cleaned_data)
