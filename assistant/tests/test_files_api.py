# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBytes, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import Optional, Tuple, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.delete_file_response import DeleteFileResponse  # noqa: F401
from assistant.models.list_files_response import ListFilesResponse  # noqa: F401
from assistant.models.open_ai_file import OpenAIFile  # noqa: F401


def test_create_file(client: TestClient):
    """Test case for create_file

    Upload a file that can be used across various endpoints. Individual files can be up to 512 MB, and the size of all files uploaded by one organization can be up to 100 GB.  The Assistants API supports files up to 2 million tokens and of specific file types. See the [Assistants Tools guide](/docs/assistants/tools) for details.  The Fine-tuning API only supports `.jsonl` files. The input also has certain required formats for fine-tuning [chat](/docs/api-reference/fine-tuning/chat-input) or [completions](/docs/api-reference/fine-tuning/completions-input) models.  The Batch API only supports `.jsonl` files up to 200 MB in size. The input also has a specific required [format](/docs/api-reference/batch/request-input).  Please [contact us](https://help.openai.com/) if you need to increase these storage limits. 
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "file": '/path/to/file',
        "purpose": 'purpose_example'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/files",
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_file(client: TestClient):
    """Test case for delete_file

    Delete a file.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/files/{file_id}".format(file_id='file_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_download_file(client: TestClient):
    """Test case for download_file

    Returns the contents of the specified file.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/files/{file_id}/content".format(file_id='file_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_files(client: TestClient):
    """Test case for list_files

    Returns a list of files.
    """
    params = [("purpose", 'purpose_example'),     ("limit", 10000),     ("order", desc),     ("after", 'after_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/files",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_file(client: TestClient):
    """Test case for retrieve_file

    Returns information about a specific file.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/files/{file_id}".format(file_id='file_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

