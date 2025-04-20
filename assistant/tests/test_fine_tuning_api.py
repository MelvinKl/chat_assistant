# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import Dict, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.create_fine_tuning_checkpoint_permission_request import CreateFineTuningCheckpointPermissionRequest  # noqa: F401
from assistant.models.create_fine_tuning_job_request import CreateFineTuningJobRequest  # noqa: F401
from assistant.models.delete_fine_tuning_checkpoint_permission_response import DeleteFineTuningCheckpointPermissionResponse  # noqa: F401
from assistant.models.fine_tuning_job import FineTuningJob  # noqa: F401
from assistant.models.list_fine_tuning_checkpoint_permission_response import ListFineTuningCheckpointPermissionResponse  # noqa: F401
from assistant.models.list_fine_tuning_job_checkpoints_response import ListFineTuningJobCheckpointsResponse  # noqa: F401
from assistant.models.list_fine_tuning_job_events_response import ListFineTuningJobEventsResponse  # noqa: F401
from assistant.models.list_paginated_fine_tuning_jobs_response import ListPaginatedFineTuningJobsResponse  # noqa: F401


def test_cancel_fine_tuning_job(client: TestClient):
    """Test case for cancel_fine_tuning_job

    Immediately cancel a fine-tune job. 
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/fine_tuning/jobs/{fine_tuning_job_id}/cancel".format(fine_tuning_job_id='ft-AF1WoRqd3aJAHsqc9NY7iL8F'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_fine_tuning_checkpoint_permission(client: TestClient):
    """Test case for create_fine_tuning_checkpoint_permission

    **NOTE:** Calling this endpoint requires an [admin API key](../admin-api-keys).  This enables organization owners to share fine-tuned models with other projects in their organization. 
    """
    create_fine_tuning_checkpoint_permission_request = {"project_ids":["project_ids","project_ids"]}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/fine_tuning/checkpoints/{permission_id}/permissions".format(permission_id='ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd'),
    #    headers=headers,
    #    json=create_fine_tuning_checkpoint_permission_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_create_fine_tuning_job(client: TestClient):
    """Test case for create_fine_tuning_job

    Creates a fine-tuning job which begins the process of creating a new model from a given dataset.  Response includes details of the enqueued job including job status and the name of the fine-tuned models once complete.  [Learn more about fine-tuning](/docs/guides/fine-tuning) 
    """
    create_fine_tuning_job_request = {"training_file":"file-abc123","metadata":{"key":"metadata"},"seed":42,"method":{"supervised":{"hyperparameters":{"batch_size":"auto","n_epochs":"auto","learning_rate_multiplier":"auto"}},"dpo":{"hyperparameters":{"beta":"auto"}},"type":"supervised"},"validation_file":"file-abc123","hyperparameters":{"batch_size":"auto","n_epochs":"auto","learning_rate_multiplier":"auto"},"model":"gpt-4o-mini","suffix":"suffix","integrations":[{"wandb":{"name":"name","project":"my-wandb-project","entity":"entity","tags":["custom-tag","custom-tag"]},"type":"wandb"},{"wandb":{"name":"name","project":"my-wandb-project","entity":"entity","tags":["custom-tag","custom-tag"]},"type":"wandb"}]}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/fine_tuning/jobs",
    #    headers=headers,
    #    json=create_fine_tuning_job_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_fine_tuning_checkpoint_permission(client: TestClient):
    """Test case for delete_fine_tuning_checkpoint_permission

    **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).  Organization owners can use this endpoint to delete a permission for a fine-tuned model checkpoint. 
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/fine_tuning/checkpoints/{permission_id}/permissions".format(permission_id='cp_zc4Q7MP6XxulcVzj4MZdwsAB'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_fine_tuning_checkpoint_permissions(client: TestClient):
    """Test case for list_fine_tuning_checkpoint_permissions

    **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).  Organization owners can use this endpoint to view all permissions for a fine-tuned model checkpoint. 
    """
    params = [("project_id", 'project_id_example'),     ("after", 'after_example'),     ("limit", 10),     ("order", descending)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/fine_tuning/checkpoints/{permission_id}/permissions".format(permission_id='ft-AF1WoRqd3aJAHsqc9NY7iL8F'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_fine_tuning_events(client: TestClient):
    """Test case for list_fine_tuning_events

    Get status updates for a fine-tuning job. 
    """
    params = [("after", 'after_example'),     ("limit", 20)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/fine_tuning/jobs/{fine_tuning_job_id}/events".format(fine_tuning_job_id='ft-AF1WoRqd3aJAHsqc9NY7iL8F'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_fine_tuning_job_checkpoints(client: TestClient):
    """Test case for list_fine_tuning_job_checkpoints

    List checkpoints for a fine-tuning job. 
    """
    params = [("after", 'after_example'),     ("limit", 10)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/fine_tuning/jobs/{fine_tuning_job_id}/checkpoints".format(fine_tuning_job_id='ft-AF1WoRqd3aJAHsqc9NY7iL8F'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_paginated_fine_tuning_jobs(client: TestClient):
    """Test case for list_paginated_fine_tuning_jobs

    List your organization's fine-tuning jobs 
    """
    params = [("after", 'after_example'),     ("limit", 20),     ("metadata", {'key': 'metadata_example'})]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/fine_tuning/jobs",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_fine_tuning_job(client: TestClient):
    """Test case for retrieve_fine_tuning_job

    Get info about a fine-tuning job.  [Learn more about fine-tuning](/docs/guides/fine-tuning) 
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/fine_tuning/jobs/{fine_tuning_job_id}".format(fine_tuning_job_id='ft-AF1WoRqd3aJAHsqc9NY7iL8F'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

