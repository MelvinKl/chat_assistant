from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Singleton

from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint
from base_component_api.impl.endpoints.default_act_endpoint import DefaultActEndpoint
from base_component_api.impl.endpoints.default_answer_endpoint import DefaultAnswerEndpoint
from base_component_api.impl.endpoints.default_get_actions_endpoint import DefaultGetActionsEndpoint
from base_component_api.impl import component_api_implementation


class DependencyContainer(DeclarativeContainer):

    wiring_config = WiringConfiguration(modules=[component_api_implementation])

    config = Configuration(yaml_files=["config.yml"])

    act_endpoint = Singleton(DefaultActEndpoint)
    answer_endpoint = Singleton(DefaultAnswerEndpoint)
    get_actions_endpoint = Singleton(
        DefaultGetActionsEndpoint,
        answer_endpoint_implementation=answer_endpoint,
        act_endpoint_implementation=act_endpoint,
    )
    upload_document_endpoint = Singleton(UploadDocumentEndpoint)
