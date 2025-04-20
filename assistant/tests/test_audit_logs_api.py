# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictInt, StrictStr  # noqa: F401
from typing import List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from assistant.models.audit_log_event_type import AuditLogEventType  # noqa: F401
from assistant.models.list_audit_logs_effective_at_parameter import ListAuditLogsEffectiveAtParameter  # noqa: F401
from assistant.models.list_audit_logs_response import ListAuditLogsResponse  # noqa: F401


def test_list_audit_logs(client: TestClient):
    """Test case for list_audit_logs

    List user actions and configuration changes within this organization.
    """
    params = [("effective_at", assistant.ListAuditLogsEffectiveAtParameter()),     ("project_ids", ['project_ids_example']),     ("event_types", [assistant.AuditLogEventType()]),     ("actor_ids", ['actor_ids_example']),     ("actor_emails", ['actor_emails_example']),     ("resource_ids", ['resource_ids_example']),     ("limit", 20),     ("after", 'after_example'),     ("before", 'before_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/organization/audit_logs",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

