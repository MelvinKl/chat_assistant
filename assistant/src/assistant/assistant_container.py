from assistant.impl.graph.chat_graph import ChatGraph
from assistant.impl.settings.mcp_server_settings import MCPSettings
from base_library.impl.settings.openai_settings import OpenAISetttings
import inject
from base_library.impl.settings.llm_settings import LLMSetttings
from base_library.impl.settings.ollama_settings import OllamaSettings
from inject import Binder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI


def _di_config(binder: Binder):
    settings_openai = OpenAISetttings()
    binder.bind(
        BaseChatModel,
        ChatOpenAI(
            model=settings_openai.model,
            base_url=settings_openai.url,
            api_key=settings_openai.openai_api_key,
        ),
    )
    binder.bind_to_constructor(MCPSettings, MCPSettings)
    binder.bind_to_constructor(ChatGraph, ChatGraph)


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
