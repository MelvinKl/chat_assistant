# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBytes, StrictStr, field_validator  # noqa: F401
from typing import Optional, Tuple, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.create_image_edit_request_model import CreateImageEditRequestModel  # noqa: F401
from assistant.models.create_image_request import CreateImageRequest  # noqa: F401
from assistant.models.images_response import ImagesResponse  # noqa: F401


def test_create_image(client: TestClient):
    """Test case for create_image

    Creates an image given a prompt.
    """
    create_image_request = {"response_format":"url","size":"1024x1024","model":"dall-e-3","style":"vivid","prompt":"A cute baby sea otter","user":"user-1234","n":1,"quality":"standard"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/images/generations",
    #    headers=headers,
    #    json=create_image_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_image_edit(client: TestClient):
    """Test case for create_image_edit

    Creates an edited or extended image given an original image and a prompt.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "image": '/path/to/file',
        "prompt": 'prompt_example',
        "mask": '/path/to/file',
        "model": assistant.CreateImageEditRequestModel(),
        "n": 1,
        "size": 1024x1024,
        "response_format": url,
        "user": 'user_example'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/images/edits",
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_image_variation(client: TestClient):
    """Test case for create_image_variation

    Creates a variation of a given image.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "image": '/path/to/file',
        "model": assistant.CreateImageEditRequestModel(),
        "n": 1,
        "response_format": url,
        "size": 1024x1024,
        "user": 'user_example'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/images/variations",
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

