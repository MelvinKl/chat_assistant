from inspect import getdoc

import inject

from base_component_api.endpoints.assist_endpoint import AssistEndpoint
from base_component_api.endpoints.get_description_endpoint import GetDescriptionEndpoint


class DefaultGetDescriptionsEndpoint(GetDescriptionEndpoint):

    @inject.autoparams()
    def __init__(self, assist_endpoint_implementation: AssistEndpoint) -> None:
        description_dict = {}
        description_dict["description"] = getdoc(assist_endpoint_implementation)
        # TODO: description_dict["name"]
        self._description_dict = description_dict

    def get_description(self) -> dict:
        return self._description_dict
