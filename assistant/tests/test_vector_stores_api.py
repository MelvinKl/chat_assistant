# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.create_vector_store_file_batch_request import CreateVectorStoreFileBatchRequest  # noqa: F401
from assistant.models.create_vector_store_file_request import CreateVectorStoreFileRequest  # noqa: F401
from assistant.models.create_vector_store_request import CreateVectorStoreRequest  # noqa: F401
from assistant.models.delete_vector_store_file_response import DeleteVectorStoreFileResponse  # noqa: F401
from assistant.models.delete_vector_store_response import DeleteVectorStoreResponse  # noqa: F401
from assistant.models.list_vector_store_files_response import ListVectorStoreFilesResponse  # noqa: F401
from assistant.models.list_vector_stores_response import ListVectorStoresResponse  # noqa: F401
from assistant.models.update_vector_store_file_attributes_request import (
    UpdateVectorStoreFileAttributesRequest,
)  # noqa: F401
from assistant.models.update_vector_store_request import UpdateVectorStoreRequest  # noqa: F401
from assistant.models.vector_store_file_batch_object import VectorStoreFileBatchObject  # noqa: F401
from assistant.models.vector_store_file_content_response import VectorStoreFileContentResponse  # noqa: F401
from assistant.models.vector_store_file_object import VectorStoreFileObject  # noqa: F401
from assistant.models.vector_store_object import VectorStoreObject  # noqa: F401
from assistant.models.vector_store_search_request import VectorStoreSearchRequest  # noqa: F401
from assistant.models.vector_store_search_results_page import VectorStoreSearchResultsPage  # noqa: F401


def test_cancel_vector_store_file_batch(client: TestClient):
    """Test case for cancel_vector_store_file_batch

    Cancel a vector store file batch. This attempts to cancel the processing of files in this batch as soon as possible.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel".format(vector_store_id='vector_store_id_example', batch_id='batch_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_create_vector_store(client: TestClient):
    """Test case for create_vector_store

    Create a vector store.
    """
    create_vector_store_request = {
        "chunking_strategy": {"type": "auto"},
        "metadata": {"key": "metadata"},
        "expires_after": {"anchor": "last_active_at", "days": 339},
        "file_ids": ["file_ids", "file_ids", "file_ids", "file_ids", "file_ids"],
        "name": "name",
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/vector_stores",
    #    headers=headers,
    #    json=create_vector_store_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_create_vector_store_file(client: TestClient):
    """Test case for create_vector_store_file

    Create a vector store file by attaching a [File](/docs/api-reference/files) to a [vector store](/docs/api-reference/vector-stores/object).
    """
    create_vector_store_file_request = {
        "chunking_strategy": {"type": "auto"},
        "file_id": "file_id",
        "attributes": {"key": "VectorStoreFileAttributes_value"},
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/vector_stores/{vector_store_id}/files".format(vector_store_id='vs_abc123'),
    #    headers=headers,
    #    json=create_vector_store_file_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_create_vector_store_file_batch(client: TestClient):
    """Test case for create_vector_store_file_batch

    Create a vector store file batch.
    """
    create_vector_store_file_batch_request = {
        "chunking_strategy": {"type": "auto"},
        "file_ids": ["file_ids", "file_ids", "file_ids", "file_ids", "file_ids"],
        "attributes": {"key": "VectorStoreFileAttributes_value"},
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/vector_stores/{vector_store_id}/file_batches".format(vector_store_id='vs_abc123'),
    #    headers=headers,
    #    json=create_vector_store_file_batch_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_delete_vector_store(client: TestClient):
    """Test case for delete_vector_store

    Delete a vector store.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "DELETE",
    #    "/vector_stores/{vector_store_id}".format(vector_store_id='vector_store_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_delete_vector_store_file(client: TestClient):
    """Test case for delete_vector_store_file

    Delete a vector store file. This will remove the file from the vector store but the file itself will not be deleted. To delete the file, use the [delete file](/docs/api-reference/files/delete) endpoint.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "DELETE",
    #    "/vector_stores/{vector_store_id}/files/{file_id}".format(vector_store_id='vector_store_id_example', file_id='file_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_vector_store(client: TestClient):
    """Test case for get_vector_store

    Retrieves a vector store.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/vector_stores/{vector_store_id}".format(vector_store_id='vector_store_id_example'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_vector_store_file(client: TestClient):
    """Test case for get_vector_store_file

    Retrieves a vector store file.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/vector_stores/{vector_store_id}/files/{file_id}".format(vector_store_id='vs_abc123', file_id='file-abc123'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_get_vector_store_file_batch(client: TestClient):
    """Test case for get_vector_store_file_batch

    Retrieves a vector store file batch.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/vector_stores/{vector_store_id}/file_batches/{batch_id}".format(vector_store_id='vs_abc123', batch_id='vsfb_abc123'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_files_in_vector_store_batch(client: TestClient):
    """Test case for list_files_in_vector_store_batch

    Returns a list of vector store files in a batch.
    """
    params = [
        ("limit", 20),
        ("order", desc),
        ("after", "after_example"),
        ("before", "before_example"),
        ("filter", "filter_example"),
    ]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/vector_stores/{vector_store_id}/file_batches/{batch_id}/files".format(vector_store_id='vector_store_id_example', batch_id='batch_id_example'),
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_vector_store_files(client: TestClient):
    """Test case for list_vector_store_files

    Returns a list of vector store files.
    """
    params = [
        ("limit", 20),
        ("order", desc),
        ("after", "after_example"),
        ("before", "before_example"),
        ("filter", "filter_example"),
    ]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/vector_stores/{vector_store_id}/files".format(vector_store_id='vector_store_id_example'),
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_list_vector_stores(client: TestClient):
    """Test case for list_vector_stores

    Returns a list of vector stores.
    """
    params = [("limit", 20), ("order", desc), ("after", "after_example"), ("before", "before_example")]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/vector_stores",
    #    headers=headers,
    #    params=params,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_modify_vector_store(client: TestClient):
    """Test case for modify_vector_store

    Modifies a vector store.
    """
    update_vector_store_request = {
        "metadata": {"key": "metadata"},
        "expires_after": {"anchor": "last_active_at", "days": 30},
        "name": "name",
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/vector_stores/{vector_store_id}".format(vector_store_id='vector_store_id_example'),
    #    headers=headers,
    #    json=update_vector_store_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_retrieve_vector_store_file_content(client: TestClient):
    """Test case for retrieve_vector_store_file_content

    Retrieve the parsed contents of a vector store file.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "GET",
    #    "/vector_stores/{vector_store_id}/files/{file_id}/content".format(vector_store_id='vs_abc123', file_id='file-abc123'),
    #    headers=headers,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_search_vector_store(client: TestClient):
    """Test case for search_vector_store

    Search a vector store for relevant chunks based on a query and file attributes filter.
    """
    vector_store_search_request = {
        "max_num_results": 4,
        "ranking_options": {"score_threshold": 0.6027456183070403, "ranker": "auto"},
        "query": "VectorStoreSearchRequest_query",
        "rewrite_query": 0,
        "filters": {"type": "eq", "value": "ComparisonFilter_value", "key": "key"},
    }

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/vector_stores/{vector_store_id}/search".format(vector_store_id='vs_abc123'),
    #    headers=headers,
    #    json=vector_store_search_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200


def test_update_vector_store_file_attributes(client: TestClient):
    """Test case for update_vector_store_file_attributes

    Update attributes on a vector store file.
    """
    update_vector_store_file_attributes_request = {"attributes": {"key": "VectorStoreFileAttributes_value"}}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    # response = client.request(
    #    "POST",
    #    "/vector_stores/{vector_store_id}/files/{file_id}".format(vector_store_id='vs_abc123', file_id='file-abc123'),
    #    headers=headers,
    #    json=update_vector_store_file_attributes_request,
    # )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
