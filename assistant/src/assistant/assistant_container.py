import inject
from base_library.impl.settings.llm_settings import LLMSetttings
from base_library.impl.settings.ollama_settings import OllamaSettings
from inject import Binder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama


def _di_config(binder: Binder):
    settings_llm = LLMSetttings()

    match settings_llm.provider:
        case "ollama":
            settings_ollama = OllamaSettings()
            binder.bind(
                BaseChatModel,
                ChatOllama(
                    model=settings_ollama.model,
                    base_url=settings_ollama.url,
                ),
            )
        case _:
            raise NotImplementedError("Configured LLM is not implemented")


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
