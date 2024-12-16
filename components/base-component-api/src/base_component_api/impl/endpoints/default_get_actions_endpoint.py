from inspect import getdoc
from tracely import trace_event

from base_component_api.endpoints.act_endpoint import ActEndpoint
from base_component_api.endpoints.answer_endpoint import AnswerEndpoint
from base_component_api.endpoints.get_actions_endpoint import GetActionsEndpoint


class DefaultGetActionsEndpoint(GetActionsEndpoint):

    def __init__(
        self, answer_endpoint_implementation: AnswerEndpoint, act_endpoint_implementation: ActEndpoint
    ) -> None:
        action_dict = {}
        if answer_endpoint_implementation.available:
            action_dict["answer"] = getdoc(answer_endpoint_implementation)

        if act_endpoint_implementation.available:
            action_dict["act"] = getdoc(act_endpoint_implementation)

        self._action_dict = action_dict

    @trace_event
    def get_actions(self) -> dict:
        return self._action_dict
