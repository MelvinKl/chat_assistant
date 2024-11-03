import inject

from base_component_api.endpoints.get_description_endpoint import GetDescriptionEndpoint
from base_component_api.impl.settings.api_settings import APISetttings
from base_component_api.models.description import Description


class DefaultGetDescriptionsEndpoint(GetDescriptionEndpoint):

    @inject.autoparams()
    def get_description(self, settings: APISetttings) -> Description:
        return Description(name=settings.name, description=settings.description)
