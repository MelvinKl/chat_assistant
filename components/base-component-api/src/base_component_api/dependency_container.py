import inject

from base_component_api.endpoints.assist_endpoint import AssistEndpoint
from base_component_api.endpoints.get_description_endpoint import GetDescriptionEndpoint
from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint
from base_component_api.impl.endpoints.default_assist_endpoint import (
    DefaultAnswerEndpoint,
)
from base_component_api.impl.endpoints.default_get_description_endpoint import (
    DefaultGetDescriptionsEndpoint,
)


def base_config(binder):
    binder.bind_to_constructor(AssistEndpoint, DefaultAnswerEndpoint)
    binder.bind_to_constructor(GetDescriptionEndpoint, DefaultGetDescriptionsEndpoint)
    binder.bind_to_constructor(UploadDocumentEndpoint, UploadDocumentEndpoint)


def configure():
    inject.configure(
        base_config,
        allow_override=True,
    )
