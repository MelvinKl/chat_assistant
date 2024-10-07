from fastembed import TextEmbedding
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Singleton
from impl.endpoints.rag_answer_endpoint import RagAnswerEndpoint
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings
from langchain.llms import Ollama

from base_library.impl.document_extractor.pdf_extractor import PDFExtractor
from base_library.impl.settings.qdrant_settings import QdrantSetttings
from base_library.impl.vector_database.qdrant_database import QdrantDatabase
from base_component_api.impl.endpoints.default_act_endpoint import DefaultActEndpoint
from base_component_api.impl.endpoints.default_answer_endpoint import DefaultAnswerEndpoint
from base_component_api.impl.endpoints.default_get_actions_endpoint import DefaultGetActionsEndpoint

from impl.endpoints.rag_upload_document_endpoint import RagUploadDocument


class RagDependencyContainer(DeclarativeContainer):

    settings_qdrant = QdrantSetttings()

    embedder = Singleton(
        OllamaEmbeddings,
        model="llama3.2:1b",
        base_url="http://open-webui-ollama.assistant.svc.cluster.local:11434",
    )
    llm = Singleton(Ollama, model="llama3.2:1b", base_url="http://open-webui-ollama.assistant.svc.cluster.local:11434")

    qdrant = Singleton(
        QdrantClient,
        url=settings_qdrant.url,
    )
    vector_database = Singleton(
        QdrantDatabase,
        embedder=embedder,
        collection_name=settings_qdrant.collection_name,
        qdrant=qdrant,
    )

    pdf_extractor = Singleton(PDFExtractor)

    act_endpoint = Singleton(DefaultActEndpoint)
    answer_endpoint = Singleton(
        RagAnswerEndpoint,
        vector_database=vector_database,
        llm=llm,
    )
    get_actions_endpoint = Singleton(
        DefaultGetActionsEndpoint,
        answer_endpoint_implementation=answer_endpoint,
        act_endpoint_implementation=act_endpoint,
    )
    upload_document_endpoint = Singleton(
        RagUploadDocument,
        pdf_extractor=pdf_extractor,
        vector_database=vector_database,
    )
