import inject
from base_component_api.dependency_container import base_config
from base_component_api.endpoints.assist_endpoint import AssistEndpoint

from base_library.impl.settings.llm_settings import LLMSetttings
from base_library.impl.settings.ollama_settings import OllamaSettings

from inject import Binder
from langchain_community.llms import Ollama
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.language_models.llms import LLM
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient

from impl.endpoints.home_assist_assist_endpoint import HomeAssistAssistEndpoint



def _di_config(binder: Binder):
    binder.install(base_config)
    settings_llm = LLMSetttings()

    match settings_llm.provider:
        case "ollama":
            settings_ollama = OllamaSettings()
            binder.bind(
                Embeddings,
                OllamaEmbeddings(
                    model=settings_ollama.model,
                    base_url=settings_ollama.url,
                ),
            )
            binder.bind(
                LLM,
                Ollama(
                    model=settings_ollama.model,
                    base_url=settings_ollama.url,
                ),
            )
        case _:
            raise NotImplementedError("Configured LLM is not implemented")

    
    
    binder.bind_to_constructor(AssistEndpoint, HomeAssistAssistEndpoint)
    


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
