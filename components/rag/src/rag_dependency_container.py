from base_library.document_extractor.extractor import Extractor
from base_library.vector_database.vector_database import VectorDatabase
import inject
from base_component_api.endpoints.act_endpoint import ActEndpoint
from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.endpoints.get_actions_endpoint import \
    GetActionsEndpoint
from base_component_api.endpoints.upload_document_endpoint import \
    UploadDocumentEndpoint
from base_component_api.impl.endpoints.default_act_endpoint import \
    DefaultActEndpoint
from base_component_api.impl.endpoints.default_answer_endpoint import \
    DefaultAnswerEndpoint
from base_component_api.impl.endpoints.default_get_actions_endpoint import \
    DefaultGetActionsEndpoint
from base_library.impl.document_extractor.pdf_extractor import PDFExtractor
from base_library.impl.settings.llm_settings import LLMSetttings
from base_library.impl.settings.ollama_settings import OllamaSettings
from base_library.impl.settings.qdrant_settings import QdrantSetttings
from base_library.impl.vector_database.qdrant_database import QdrantDatabase
from fastembed import TextEmbedding
from impl.endpoints.rag_answer_endpoint import RagAnswerEndpoint
from impl.endpoints.rag_upload_document_endpoint import RagUploadDocument
from langchain.llms import Ollama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.language_models.llms import LLM
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from base_component_api.dependency_container import base_config

def _di_config(binder):
    binder.install(base_config)
    settings_llm = LLMSetttings()
    settings_qdrant = QdrantSetttings()

    binder.bind_to_constructor(QdrantSetttings, QdrantSetttings)        
    binder.bind(QdrantClient,QdrantClient(url=settings_qdrant.url))


    match settings_llm.provider:
        case "ollama":
            settings_ollama = OllamaSettings()
            binder.bind(Embeddings, OllamaEmbeddings(model=settings_ollama.model,
                base_url=settings_ollama.url,
            ))
            binder.bind(LLM, Ollama(model=settings_ollama.model,
                base_url=settings_ollama.url,))
        case _:
            raise NotImplementedError("Configured LLM is not implemented")
    

    binder.bind_to_constructor(VectorDatabase,lambda: QdrantDatabase(
        collection_name=settings_qdrant.collection_name,
        url=settings_qdrant.url,
    ))

    binder.bind_to_constructor(Extractor,PDFExtractor)
    binder.bind_to_constructor(AnswerEndpoint,RagAnswerEndpoint)
    binder.bind_to_constructor(UploadDocumentEndpoint,RagUploadDocument)
    
def configure():
    inject.configure(_di_config, allow_override=True, clear=True)