import inject
from base_library.vector_database.vector_database import VectorDatabase
from langchain_community.vectorstores import Qdrant
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.documents import Document
from langchain_core.embeddings.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


class QdrantDatabase(VectorDatabase):

    @inject.autoparams("embedder", "qdrant")
    def __init__(
        self,
        embedder:Embeddings,
        collection_name: str,
        qdrant: QdrantClient,
        url: str,
    ):
        self._qdrant = qdrant
        self._url = url
        self._embedder = embedder
        self._collection = collection_name       
        self._client = Qdrant(
            client=qdrant,
            collection_name=collection_name,
            embeddings=embedder,
        )

    def upload_documents(self, documents: list[Document]) -> None:
        Qdrant.from_documents(
            documents,
            self._embedder,
            collection_name=self._collection,
            url=self._url,
        )        
        #self._client.add_documents(documents=documents)

    def search(self, query: str) -> list[Document]:
        retriever = self._client.as_retriever(
            query=query,
        )
        return retriever.invoke(query)
        return self._client.similarity_search(query)

    @property
    def retriever(self):
        return self._client.as_retriever()
