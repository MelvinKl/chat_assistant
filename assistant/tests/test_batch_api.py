# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr  # noqa: F401
from typing import Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.batch import Batch  # noqa: F401
from assistant.models.create_batch_request import CreateBatchRequest  # noqa: F401
from assistant.models.list_batches_response import ListBatchesResponse  # noqa: F401


def test_cancel_batch(client: TestClient):
    """Test case for cancel_batch

    Cancels an in-progress batch. The batch will be in status `cancelling` for up to 10 minutes, before changing to `cancelled`, where it will have partial results (if any) available in the output file.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/batches/{batch_id}/cancel".format(batch_id='batch_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_batch(client: TestClient):
    """Test case for create_batch

    Creates and executes a batch from an uploaded file of requests
    """
    create_batch_request = assistant.CreateBatchRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/batches",
    #    headers=headers,
    #    json=create_batch_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_batches(client: TestClient):
    """Test case for list_batches

    List your organization's batches.
    """
    params = [("after", 'after_example'),     ("limit", 20)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/batches",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_batch(client: TestClient):
    """Test case for retrieve_batch

    Retrieves a batch.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/batches/{batch_id}".format(batch_id='batch_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

