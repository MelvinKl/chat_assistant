import inject
from base_component_api.dependency_container import base_config
from base_component_api.endpoints.assist_endpoint import AssistEndpoint
from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint
from base_library.document_extractor.extractor import Extractor
from base_library.impl.document_extractor.pdf_extractor import PDFExtractor
from base_library.impl.settings.llm_settings import LLMSetttings
from base_library.impl.settings.ollama_settings import OllamaSettings
from base_library.impl.settings.qdrant_settings import QdrantSetttings
from base_library.impl.vector_database.qdrant_database import QdrantDatabase
from base_library.vector_database.vector_database import VectorDatabase
from langchain.llms import Ollama
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.language_models.llms import LLM
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient

from impl.endpoints.rag_assist_endpoint import RagAssistEndpoint
from impl.endpoints.rag_upload_document_endpoint import RagUploadDocument


def _di_config(binder):
    binder.install(base_config)
    settings_llm = LLMSetttings()
    settings_qdrant = QdrantSetttings()

    binder.bind_to_constructor(QdrantSetttings, QdrantSetttings)
    binder.bind(QdrantClient, QdrantClient(url=settings_qdrant.url))

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

    binder.bind_to_constructor(
        VectorDatabase,
        lambda: QdrantDatabase(
            collection_name=settings_qdrant.collection_name,
            url=settings_qdrant.url,
        ),
    )

    binder.bind_to_constructor(Extractor, PDFExtractor)
    binder.bind_to_constructor(AssistEndpoint, RagAssistEndpoint)
    binder.bind_to_constructor(UploadDocumentEndpoint, RagUploadDocument)


def configure():
    inject.configure(_di_config, allow_override=True, clear=True)
