
from base_component_api.endpoints.act_endpoint import ActEndpoint


class DefaultActEndpoint(ActEndpoint):

    async def aact(self, request)->str:
        raise NotImplementedError()
