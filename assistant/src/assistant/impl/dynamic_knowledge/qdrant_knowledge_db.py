import asyncio
from datetime import datetime

import inject
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models

from assistant.impl.dynamic_knowledge.knowledge_checker import KnowledgeChecker
from assistant.impl.mapper.knowledge_mapper import KnowledgeMapper
from assistant.impl.settings.dynamic_knowledge_settings import DynamicKnowledgeSettings
from assistant.interfaces.knowledge import Knowledge
from assistant.interfaces.knowledge_db import KnowledgeDB
from qdrant_client.models import VectorParams, Distance

class QdrantKnowledgeDB(KnowledgeDB):
    @inject.autoparams()
    def __init__(
        self,
        mapper: KnowledgeMapper,
        knowledge_checker: KnowledgeChecker,
        embedder: OpenAIEmbeddings,
        vectordb_client: QdrantClient,
        settings: DynamicKnowledgeSettings,
    ):
        self._mapper = mapper
        self._settings = settings
        self._embedder = embedder
        self._knowledge_checker = knowledge_checker
        self._vectordb_client = vectordb_client
        
        if not settings.collection_name in [x.name for x in vectordb_client.get_collections().collections]:
            _ = vectordb_client.create_collection(
                self._settings.collection_name,
                vectors_config=VectorParams(
                    size=len(self._embedder.embed_documents(["hello"])[0]), distance=Distance.COSINE
                ),
            )

        vectorstore = QdrantVectorStore(
            client=vectordb_client,
            collection_name=settings.collection_name,
            embedding=embedder,
        )
        self._vectorstore = vectorstore

    async def aretrieve_knowledge(self, query: str) -> list[Knowledge]:
        filter_kwargs = models.Filter(
            must_not=[
                models.FieldCondition(
                    key="metadata.expiration_date",
                    range=models.DatetimeRange(
                        gt=datetime.now(),
                        gte=None,
                        lt=None,
                        lte=None,
                    ),
                )
            ]
        )
        result_docs = await self._vectorstore.asearch(
            query=query,
            filter_kwargs=filter_kwargs,
            search_kwargs={"k": self._settings.max_items, "score_threshold": self._settings.score_threshold},
        ).ainvoke(query)
        return [self._mapper.from_document(x) for x in result_docs]

    async def aupdate_knowledge(self, conversation: list[str]) -> None:
        retrieved_knowledge = await self.aretrieve_knowledge(conversation[-2])
        new_knowledge, updated_knowledge, outdated_knowledge = await self._knowledge_checker.acheck_knowledge(
            conversation, retrieved_knowledge
        )

        tasks = [self._aupsert_documents(self._mapper.to_document(x)) for x in new_knowledge]
        tasks += [self._aupsert_documents(self._mapper.to_document(x)) for x in updated_knowledge]
        tasks += [self._adelete_documents(self._mapper.to_document(x)) for x in outdated_knowledge]

        await asyncio.wait(tasks)

    async def adelete_outdated_knowledge(self) -> None:
        earch_kwargs = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.expiration_date",
                    range=models.DatetimeRange(
                        gt=datetime.now(),
                        gte=None,
                        lt=None,
                        lte=None,
                    ),
                )
            ]
        )
        search_results = self._vectorstore.client.scroll(
            collection_name=self._vectorstore.collection_name, scroll_filter=models.Filter(earch_kwargs)
        )
        if not search_results:
            return

        outdated_documents: list[Document] = [
            Document(
                page_content=search_result.payload["page_content"],
                metadata=search_result.payload["metadata"],
            )
            for search_result in search_results[0]
        ]
        tasks = [self._adelete_documents(self._mapper.to_document(x)) for x in outdated_documents]
        await asyncio.wait(tasks)

    async def _adelete_documents(self, document: Document) -> None:
        points_selector = models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.id",
                        match=models.MatchValue(value=document.metadata["id"]),
                    )
                ],
            )
        )

        self._vectorstore.client.delete(
            collection_name=self._settings.collection_name,
            points_selector=points_selector,
        )

    async def _aupsert_documents(self, document: Document) -> None:
        collection = self._db_client.get_collection(self._settings.collection_name)
        collection.add(
            ids=[document.metadata["id"]],
            documents=[document.page_content],
            metadatas=[document.metadata],
        )
