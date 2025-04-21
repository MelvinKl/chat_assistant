from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import BaseModel

class MCPServer(BaseModel):
    url: str
    name: str

class MCPSettings(BaseSettings):
    class Config:
        env_prefix = "SETTINGS_MCP_"

    servers: list[MCPServer] = Field()
