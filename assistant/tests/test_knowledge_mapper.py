"""Unit tests for knowledge_mapper.py"""

from datetime import datetime
from uuid import uuid4

import pytest
from langchain_core.documents import Document

from assistant.impl.mapper.knowledge_mapper import KnowledgeMapper
from assistant.interfaces.knowledge import Knowledge


@pytest.fixture
def knowledge_mapper():
    """Create KnowledgeMapper instance."""
    return KnowledgeMapper()


def test_to_document_creates_document_from_knowledge(knowledge_mapper):
    """Test converting Knowledge to Document."""
    knowledge_id = uuid4()
    expiration = datetime.now()
    knowledge = Knowledge(
        information="Test information",
        uuid=knowledge_id,
        expiration_date=expiration,
    )

    document = knowledge_mapper.to_document(knowledge)

    assert document.page_content == "Test information"
    assert document.metadata["id"] == knowledge_id
    assert document.metadata["expiration_date"] == expiration
    assert document.id == str(knowledge_id)


def test_to_document_generates_uuid_if_missing(knowledge_mapper):
    """Test that UUID is generated if not provided."""
    knowledge = Knowledge(
        information="Test",
        uuid=None,
        expiration_date=None,
    )

    document = knowledge_mapper.to_document(knowledge)

    assert document.metadata["id"] is not None
    assert knowledge.uuid is not None  # Mutates input


def test_from_document_creates_knowledge_from_document(knowledge_mapper):
    """Test converting Document to Knowledge."""
    doc_id = uuid4()
    expiration = datetime.now()
    document = Document(
        page_content="Test content",
        metadata={
            "id": doc_id,
            "expiration_date": expiration,
        },
        id=str(doc_id),
    )

    knowledge = knowledge_mapper.from_document(document)

    assert knowledge.information == "Test content"
    assert knowledge.uuid == doc_id
    assert knowledge.expiration_date == expiration


def test_roundtrip_knowledge_to_document_to_knowledge(knowledge_mapper):
    """Test roundtrip conversion preserves data."""
    original_knowledge = Knowledge(
        information="Important fact",
        uuid=uuid4(),
        expiration_date=datetime.now(),
    )

    document = knowledge_mapper.to_document(original_knowledge)
    recovered_knowledge = knowledge_mapper.from_document(document)

    assert recovered_knowledge.information == original_knowledge.information
    assert recovered_knowledge.uuid == original_knowledge.uuid
    assert recovered_knowledge.expiration_date == original_knowledge.expiration_date
