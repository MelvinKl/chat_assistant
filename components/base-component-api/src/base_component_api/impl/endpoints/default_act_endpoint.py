from tracely import trace_event
from base_component_api.endpoints.act_endpoint import ActEndpoint


class DefaultActEndpoint(ActEndpoint):

    @property
    def available(self) -> bool:
        return False


    @trace_event()
    async def aact(self, request) -> str:
        raise NotImplementedError()
