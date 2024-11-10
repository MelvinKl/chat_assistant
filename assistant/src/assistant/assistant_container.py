import inject
from base_library.impl.settings.llm_settings import LLMSetttings
from base_library.impl.settings.ollama_settings import OllamaSettings
from base_library.impl.vector_database.qdrant_database import QdrantDatabase
from base_library.vector_database.vector_database import VectorDatabase
from inject import Binder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama


def _di_config(binder: Binder):
    settings_llm = LLMSetttings()

    match settings_llm.provider:
        case "ollama":
            settings_ollama = OllamaSettings()
            # binder.bind(
            #    Embeddings,
            #    OllamaEmbeddings(
            #        model=settings_ollama.model,
            #        base_url=settings_ollama.url,
            #    ),
            # )
            binder.bind(
                BaseChatModel,
                ChatOllama(
                    model=settings_ollama.model,
                    base_url=settings_ollama.url,
                ),
            )
        case _:
            raise NotImplementedError("Configured LLM is not implemented")

    binder.bind_to_constructor(
        VectorDatabase,
        lambda: QdrantDatabase(
            collection_name=settings_qdrant.collection_name,
            url=settings_qdrant.url,
        ),
    )


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
