import inject
from base_component_api.endpoints.act_endpoint import ActEndpoint
from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.endpoints.get_actions_endpoint import \
    GetActionsEndpoint
from base_component_api.endpoints.upload_document_endpoint import \
    UploadDocumentEndpoint
from base_component_api.impl import component_api_implementation
from base_component_api.impl.endpoints.default_act_endpoint import \
    DefaultActEndpoint
from base_component_api.impl.endpoints.default_answer_endpoint import \
    DefaultAnswerEndpoint
from base_component_api.impl.endpoints.default_get_actions_endpoint import \
    DefaultGetActionsEndpoint


def _di_config(binder):
    #config = Configuration(yaml_files=["config.yml"])

    binder.bind_to_constructor(ActEndpoint, DefaultActEndpoint)
    binder.bind_to_constructor(AnswerEndpoint,DefaultAnswerEndpoint)
    binder.bind_to_constructor(GetActionsEndpoint,DefaultGetActionsEndpoint)
    binder.bind_to_constructor(UploadDocumentEndpoint,UploadDocumentEndpoint)
    
def configure():
    inject.configure(_di_config)