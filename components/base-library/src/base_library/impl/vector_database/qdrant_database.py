from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from qdrant_client.http.models import Distance, VectorParams


from base_library.vector_database.vector_database import VectorDatabase


class QdrantDatabase(VectorDatabase):

        
    def __init__(self, embedder,collection_name:str,qdrant:QdrantClient,):
        self._qdrant = qdrant
        self._embedder = embedder
        self._collection = collection_name
        try:
            self._qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=2048, distance=Distance.COSINE),
            )
        except Exception as e:
            pass
        self._client = QdrantVectorStore(
            client=qdrant,
            collection_name=collection_name,
            embedding=embedder,
        )        

    def upload_documents(self, documents:list[Document])->None:
        self._client.add_documents(documents=documents)

    def search(self, query:str)->list[Document]:
        return self._client.similarity_search(query)
    
    @property
    def retriever(self):
        return self._client.as_retriever()