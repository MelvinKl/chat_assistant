
from base_component_api.endpoints.act_endpoint import ActEndpoint


class DefaultActEndpoint(ActEndpoint):

    @property
    def available(self)->bool:
        return False

    async def aact(self, request)->str:
        raise NotImplementedError()
