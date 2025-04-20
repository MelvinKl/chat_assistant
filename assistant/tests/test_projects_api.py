# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBool, StrictInt, StrictStr  # noqa: F401
from typing import Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.error_response import ErrorResponse  # noqa: F401
from assistant.models.project import Project  # noqa: F401
from assistant.models.project_api_key import ProjectApiKey  # noqa: F401
from assistant.models.project_api_key_delete_response import ProjectApiKeyDeleteResponse  # noqa: F401
from assistant.models.project_api_key_list_response import ProjectApiKeyListResponse  # noqa: F401
from assistant.models.project_create_request import ProjectCreateRequest  # noqa: F401
from assistant.models.project_list_response import ProjectListResponse  # noqa: F401
from assistant.models.project_rate_limit import ProjectRateLimit  # noqa: F401
from assistant.models.project_rate_limit_list_response import ProjectRateLimitListResponse  # noqa: F401
from assistant.models.project_rate_limit_update_request import ProjectRateLimitUpdateRequest  # noqa: F401
from assistant.models.project_service_account import ProjectServiceAccount  # noqa: F401
from assistant.models.project_service_account_create_request import ProjectServiceAccountCreateRequest  # noqa: F401
from assistant.models.project_service_account_create_response import ProjectServiceAccountCreateResponse  # noqa: F401
from assistant.models.project_service_account_delete_response import ProjectServiceAccountDeleteResponse  # noqa: F401
from assistant.models.project_service_account_list_response import ProjectServiceAccountListResponse  # noqa: F401
from assistant.models.project_update_request import ProjectUpdateRequest  # noqa: F401
from assistant.models.project_user import ProjectUser  # noqa: F401
from assistant.models.project_user_create_request import ProjectUserCreateRequest  # noqa: F401
from assistant.models.project_user_delete_response import ProjectUserDeleteResponse  # noqa: F401
from assistant.models.project_user_list_response import ProjectUserListResponse  # noqa: F401
from assistant.models.project_user_update_request import ProjectUserUpdateRequest  # noqa: F401


def test_archive_project(client: TestClient):
    """Test case for archive_project

    Archives a project in the organization. Archived projects cannot be used or updated.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/projects/{project_id}/archive".format(project_id='project_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_project(client: TestClient):
    """Test case for create_project

    Create a new project in the organization. Projects can be created and archived, but cannot be deleted.
    """
    project_create_request = {"name":"name"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/projects",
    #    headers=headers,
    #    json=project_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_project_service_account(client: TestClient):
    """Test case for create_project_service_account

    Creates a new service account in the project. This also returns an unredacted API key for the service account.
    """
    project_service_account_create_request = {"name":"name"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/projects/{project_id}/service_accounts".format(project_id='project_id_example'),
    #    headers=headers,
    #    json=project_service_account_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_project_user(client: TestClient):
    """Test case for create_project_user

    Adds a user to the project. Users must already be members of the organization to be added to a project.
    """
    project_user_create_request = {"role":"owner","user_id":"user_id"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/projects/{project_id}/users".format(project_id='project_id_example'),
    #    headers=headers,
    #    json=project_user_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_project_api_key(client: TestClient):
    """Test case for delete_project_api_key

    Deletes an API key from the project.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/organization/projects/{project_id}/api_keys/{key_id}".format(project_id='project_id_example', key_id='key_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_project_service_account(client: TestClient):
    """Test case for delete_project_service_account

    Deletes a service account from the project.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/organization/projects/{project_id}/service_accounts/{service_account_id}".format(project_id='project_id_example', service_account_id='service_account_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_project_user(client: TestClient):
    """Test case for delete_project_user

    Deletes a user from the project.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/organization/projects/{project_id}/users/{user_id}".format(project_id='project_id_example', user_id='user_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_project_api_keys(client: TestClient):
    """Test case for list_project_api_keys

    Returns a list of API keys in the project.
    """
    params = [("limit", 20),     ("after", 'after_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}/api_keys".format(project_id='project_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_project_rate_limits(client: TestClient):
    """Test case for list_project_rate_limits

    Returns the rate limits per model for a project.
    """
    params = [("limit", 100),     ("after", 'after_example'),     ("before", 'before_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}/rate_limits".format(project_id='project_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_project_service_accounts(client: TestClient):
    """Test case for list_project_service_accounts

    Returns a list of service accounts in the project.
    """
    params = [("limit", 20),     ("after", 'after_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}/service_accounts".format(project_id='project_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_project_users(client: TestClient):
    """Test case for list_project_users

    Returns a list of users in the project.
    """
    params = [("limit", 20),     ("after", 'after_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}/users".format(project_id='project_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_projects(client: TestClient):
    """Test case for list_projects

    Returns a list of projects.
    """
    params = [("limit", 20),     ("after", 'after_example'),     ("include_archived", False)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_modify_project(client: TestClient):
    """Test case for modify_project

    Modifies a project in the organization.
    """
    project_update_request = {"name":"name"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/projects/{project_id}".format(project_id='project_id_example'),
    #    headers=headers,
    #    json=project_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_modify_project_user(client: TestClient):
    """Test case for modify_project_user

    Modifies a user's role in the project.
    """
    project_user_update_request = {"role":"owner"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/projects/{project_id}/users/{user_id}".format(project_id='project_id_example', user_id='user_id_example'),
    #    headers=headers,
    #    json=project_user_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_project(client: TestClient):
    """Test case for retrieve_project

    Retrieves a project.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}".format(project_id='project_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_project_api_key(client: TestClient):
    """Test case for retrieve_project_api_key

    Retrieves an API key in the project.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}/api_keys/{key_id}".format(project_id='project_id_example', key_id='key_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_project_service_account(client: TestClient):
    """Test case for retrieve_project_service_account

    Retrieves a service account in the project.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}/service_accounts/{service_account_id}".format(project_id='project_id_example', service_account_id='service_account_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_project_user(client: TestClient):
    """Test case for retrieve_project_user

    Retrieves a user in the project.
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/projects/{project_id}/users/{user_id}".format(project_id='project_id_example', user_id='user_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_update_project_rate_limits(client: TestClient):
    """Test case for update_project_rate_limits

    Updates a project rate limit.
    """
    project_rate_limit_update_request = {"batch_1_day_max_input_tokens":2,"max_tokens_per_1_minute":6,"max_images_per_1_minute":1,"max_audio_megabytes_per_1_minute":5,"max_requests_per_1_minute":0,"max_requests_per_1_day":5}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/organization/projects/{project_id}/rate_limits/{rate_limit_id}".format(project_id='project_id_example', rate_limit_id='rate_limit_id_example'),
    #    headers=headers,
    #    json=project_rate_limit_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

