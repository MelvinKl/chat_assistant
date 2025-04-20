# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBytes, StrictStr  # noqa: F401
from typing import Tuple, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.complete_upload_request import CompleteUploadRequest  # noqa: F401
from assistant.models.create_upload_request import CreateUploadRequest  # noqa: F401
from assistant.models.upload import Upload  # noqa: F401
from assistant.models.upload_part import UploadPart  # noqa: F401


def test_add_upload_part(client: TestClient):
    """Test case for add_upload_part

    Adds a [Part](/docs/api-reference/uploads/part-object) to an [Upload](/docs/api-reference/uploads/object) object. A Part represents a chunk of bytes from the file you are trying to upload.   Each Part can be at most 64 MB, and you can add Parts until you hit the Upload maximum of 8 GB.  It is possible to add multiple Parts in parallel. You can decide the intended order of the Parts when you [complete the Upload](/docs/api-reference/uploads/complete). 
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "data": '/path/to/file'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/uploads/{upload_id}/parts".format(upload_id='upload_abc123'),
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_cancel_upload(client: TestClient):
    """Test case for cancel_upload

    Cancels the Upload. No Parts may be added after an Upload is cancelled. 
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/uploads/{upload_id}/cancel".format(upload_id='upload_abc123'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_complete_upload(client: TestClient):
    """Test case for complete_upload

    Completes the [Upload](/docs/api-reference/uploads/object).   Within the returned Upload object, there is a nested [File](/docs/api-reference/files/object) object that is ready to use in the rest of the platform.  You can specify the order of the Parts by passing in an ordered list of the Part IDs.  The number of bytes uploaded upon completion must match the number of bytes initially specified when creating the Upload object. No Parts may be added after an Upload is completed. 
    """
    complete_upload_request = {"part_ids":["part_ids","part_ids"],"md5":"md5"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/uploads/{upload_id}/complete".format(upload_id='upload_abc123'),
    #    headers=headers,
    #    json=complete_upload_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_upload(client: TestClient):
    """Test case for create_upload

    Creates an intermediate [Upload](/docs/api-reference/uploads/object) object that you can add [Parts](/docs/api-reference/uploads/part-object) to. Currently, an Upload can accept at most 8 GB in total and expires after an hour after you create it.  Once you complete the Upload, we will create a [File](/docs/api-reference/files/object) object that contains all the parts you uploaded. This File is usable in the rest of our platform as a regular File object.  For certain `purpose` values, the correct `mime_type` must be specified.  Please refer to documentation for the  [supported MIME types for your use case](/docs/assistants/tools/file-search#supported-files).  For guidance on the proper filename extensions for each purpose, please follow the documentation on [creating a File](/docs/api-reference/files/create). 
    """
    create_upload_request = {"filename":"filename","purpose":"assistants","mime_type":"mime_type","bytes":0}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/uploads",
    #    headers=headers,
    #    json=create_upload_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

