"""Tests for the helm chart under infrastructure/helm.

The CI test job runs on a plain runner without helm or kubectl and without a
cluster, so these tests read the chart files (Chart.yaml, values.yaml,
templates/) and evaluate the chart's own template syntax in Python: the
helpers below implement the Go template subset the chart uses (if/else/end,
range, include/define, dict, printf, b64enc, toJson, quote, indent, and
pipeline ``|``) and render each template with the chart values.

Each test implements one scenario of requirements/helm-deployment.feature.
"""

import base64
import json
import re
from pathlib import Path

import yaml

from assistant.impl.settings.api_settings import APISetttings
from assistant.impl.settings.information_settings import InformationSettings
from assistant.impl.settings.mcp_server_settings import MCPSettings
from assistant.impl.settings.openai_settings import OpenAISetttings
from assistant.impl.settings.prompt_settings import PromptSettings
from assistant.impl.settings.subagent_settings import SubagentSettings

REPO_ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = REPO_ROOT / "infrastructure" / "helm"

# A template value reference that resolves to nothing: go templates print
# these as "<no value>", the sentinel keeps them distinguishable.
NOVALUE = object()

ACTION_PATTERN = re.compile(r"\{\{-?.*?-?\}\}", re.DOTALL)
EXPRESSION_TOKEN = re.compile(
    r'"(?P<literal>[^"]*)"'
    r"|\$(?P<variable>\w+(?:\.\w+)*)"
    r"|\.(?P<path>(?:\w+)(?:\.\w+)*)"
    r"|\.(?P<dot>)"
    r"|\|(?P<pipe>)"
    r"|\((?P<lparen>)"
    r"|\)(?P<rparen>)"
    r"|\d+(?P<number>)"
    r"|\w+(?P<word>)"
)
RANGE_VARIABLES = re.compile(r"^(?P<vars>\$\w+\s*(?:,\s*\$\w+\s*)?:=\s*)?(?P<expr>.+)$")


def tokenize(text: str) -> list[tuple]:
    """Split one template into (kind, payload, ltrim, rtrim) node tuples."""
    nodes = []
    position = 0
    for match in ACTION_PATTERN.finditer(text):
        if match.start() > position:
            nodes.append(("text", text[position : match.start()]))
        body = match.group(0)
        ltrim = body.startswith("{{-")
        rtrim = body.endswith("-}}")
        inner = body[2:-2]
        if ltrim:
            inner = inner[1:]
        if rtrim:
            inner = inner[:-1]
        nodes.append(("action", inner.strip(), ltrim, rtrim))
        position = match.end()
    if position < len(text):
        nodes.append(("text", text[position:]))
    return nodes


def apply_trims(nodes: list[tuple]) -> list[tuple]:
    """Apply the go template whitespace trimming of the action nodes."""
    for index, node in enumerate(nodes):
        kind = node[0]
        if kind != "action":
            continue
        _, _, ltrim, rtrim = node
        if ltrim and index > 0 and nodes[index - 1][0] == "text":
            previous = nodes[index - 1]
            nodes[index - 1] = ("text", previous[1].rstrip())
        if rtrim:
            for later_index in range(index + 1, len(nodes)):
                if nodes[later_index][0] == "text":
                    following = nodes[later_index][1]
                    nodes[later_index] = ("text", following.lstrip())
                    break
    return nodes


def tokenize_expression(payload: str) -> list[tuple[str, str]]:
    tokens = []
    position = 0
    while position < len(payload):
        while position < len(payload) and payload[position] in " \t":
            position += 1
        if position >= len(payload):
            break
        match = EXPRESSION_TOKEN.match(payload, position)
        if match is None:
            raise ValueError(f"cannot tokenize expression: {payload!r}")
        tokens.append((match.lastgroup, match.group()))
        position = match.end()
    return tokens


def parse_variable(text: str, index: int):
    name = text[1:]
    if "." in name:
        return ("varpath", name.split(".")[0], tuple(name.split(".")[1:])), index + 1
    return ("variable", name), index + 1


def parse_parenthesized(tokens: list[tuple[str, str]], index: int):
    node, index = parse_pipeline(tokens, index + 1)
    if index >= len(tokens) or tokens[index][0] != "rparen":
        raise ValueError("unbalanced parenthesis in expression")
    return node, index + 1


def parse_primary(tokens: list[tuple[str, str]], index: int):
    kind, text = tokens[index]
    if kind == "literal":
        return ("literal", text[1:-1]), index + 1
    if kind == "variable":
        return parse_variable(text, index)
    if kind == "dot":
        return ("ref", ()), index + 1
    if kind == "path":
        return ("ref", tuple(text.split(".")[1:])), index + 1
    if kind == "number":
        return ("number", int(text)), index + 1
    if kind == "lparen":
        return parse_parenthesized(tokens, index)
    if kind == "word":
        arguments, index = parse_arguments(tokens, index + 1)
        return ("call", text, arguments), index
    raise ValueError(f"unexpected expression token: {text!r}")


def parse_arguments(tokens: list[tuple[str, str]], index: int):
    arguments = []
    while index < len(tokens) and tokens[index][0] not in ("pipe", "rparen"):
        node, index = parse_primary(tokens, index)
        arguments.append(node)
    return arguments, index


def parse_pipeline(tokens: list[tuple[str, str]], index: int):
    node, index = parse_primary(tokens, index)
    stages = []
    while index < len(tokens) and tokens[index][0] == "pipe":
        index += 1
        stage, index = parse_primary(tokens, index)
        if stage[0] != "call":
            raise ValueError("pipeline stage must be a function call")
        stages.append((stage[1], stage[2]))
    if stages:
        node = ("pipe", node, stages)
    return node, index


def parse_expression(payload: str):
    tokens = tokenize_expression(payload)
    node, index = parse_pipeline(tokens, 0)
    if index != len(tokens):
        raise ValueError(f"trailing tokens in expression: {payload!r}")
    return node


def resolve_reference(root, path: tuple[str, ...]):
    value = root
    for part in path:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return NOVALUE
    return value


def template_dict(*pairs) -> dict:
    result = {}
    for key, value in zip(pairs[0::2], pairs[1::2]):
        result[key] = value
    return result


def b64encode_value(payload) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return base64.b64encode(payload).decode("ascii")


def indent_value(count: int, value) -> str:
    return "\n".join(" " * count + line for line in str(value).split("\n"))


def call_function(name: str, arguments: list):
    if name == "dict":
        return template_dict(*arguments)
    if name == "printf":
        return arguments[0] % tuple(arguments[1:])
    if name == "b64enc":
        return b64encode_value(arguments[0])
    if name in ("toJson", "quote"):
        return json.dumps(arguments[0])
    if name in ("indent", "nindent"):
        return indent_value(arguments[0], arguments[1])
    if name == "print":
        return render_value(arguments[0])
    raise ValueError(f"unsupported template function: {name}")


def evaluate(node, context: dict):
    kind = node[0]
    if kind in ("literal", "number"):
        return node[1]
    if kind == "variable":
        return context["variables"][node[1]]
    if kind == "varpath":
        return resolve_reference(context["variables"][node[1]], node[2])
    if kind == "ref":
        return resolve_reference(context["root"], node[1])
    if kind == "call":
        return call_function(node[1], [evaluate(argument, context) for argument in node[2]])
    if kind == "pipe":
        value = evaluate(node[1], context)
        for name, arguments in node[2]:
            value = call_function(name, [evaluate(argument, context) for argument in arguments] + [value])
        return value
    raise ValueError(f"unknown expression node: {kind!r}")


def render_value(value) -> str:
    if value is NOVALUE:
        return "<no value>"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    if value is None:
        return ""
    return str(value)


def is_truthy(value) -> bool:
    if value is NOVALUE or value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, (str, list, dict, tuple)):
        return len(value) != 0
    return True


def parse_if(nodes: list[tuple], index: int):
    expression = nodes[index][1].split(None, 1)[1].strip()
    body, index = parse_block(nodes, index + 1, frozenset({"else", "end"}))
    else_body = []
    if index < len(nodes) and nodes[index][1] == "else":
        else_body, index = parse_block(nodes, index + 1, frozenset({"end"}))
    if index >= len(nodes) or nodes[index][1] != "end":
        raise ValueError("if action without matching end")
    return ("if", expression, body, else_body), index + 1


def parse_range(nodes: list[tuple], index: int):
    payload = nodes[index][1].split(None, 1)[1]
    match = RANGE_VARIABLES.match(payload)
    if match is None:
        raise ValueError(f"bad range action: {payload}")
    if match["vars"]:
        variables = [name.strip().lstrip("$") for name in match["vars"].replace(" :=", "").split(",")]
    else:
        variables = []
    body, index = parse_block(nodes, index + 1, frozenset({"end"}))
    if index >= len(nodes) or nodes[index][1] != "end":
        raise ValueError("range action without matching end")
    return ("range", variables, match["expr"].strip(), body), index + 1


def parse_define(nodes: list[tuple], index: int):
    name = nodes[index][1].split(None, 1)[1].strip().strip('"')
    body, index = parse_block(nodes, index + 1, frozenset({"end"}))
    if index >= len(nodes) or nodes[index][1] != "end":
        raise ValueError("define action without matching end")
    return ("define", name, body), index + 1


def parse_include(nodes: list[tuple], index: int):
    tokens = tokenize_expression(nodes[index][1])
    name = tokens[1][1][1:-1]
    argument, next_index = parse_pipeline(tokens, 2)
    if next_index != len(tokens):
        raise ValueError("trailing tokens in include action")
    return ("include", name, argument), index + 1


def parse_item(nodes: list[tuple], index: int):
    kind, payload = nodes[index][0], nodes[index][1]
    if kind != "action":
        return (kind, payload), index + 1
    keyword = payload.split(None, 1)[0]
    if keyword == "if":
        return parse_if(nodes, index)
    if keyword == "range":
        return parse_range(nodes, index)
    if keyword == "define":
        return parse_define(nodes, index)
    if keyword == "include":
        return parse_include(nodes, index)
    if keyword in ("else", "end"):
        raise ValueError(f"stray {keyword} action")
    if payload.startswith("$") and ":=" in payload:
        name, expression = payload.split(":=", 1)
        return ("assign", name.strip().lstrip("$"), expression.strip()), index + 1
    return ("expr", payload), index + 1


def is_stop(node: tuple, stop_words: frozenset) -> bool:
    return node[0] == "action" and node[1].split(None, 1)[0] in stop_words


def parse_block(nodes: list[tuple], index: int, stop_words: frozenset):
    items = []
    while index < len(nodes) and not is_stop(nodes[index], stop_words):
        item, index = parse_item(nodes, index)
        items.append(item)
    return items, index


def parse_template(text: str) -> list[tuple]:
    return parse_block(apply_trims(tokenize(text)), 0, frozenset())[0]


def evaluate_item(item: tuple, context: dict, output: list[str]):
    kind = item[0]
    if kind == "text":
        output.append(item[1])
    elif kind == "expr":
        output.append(render_value(evaluate(parse_expression(item[1]), context)))
    elif kind == "assign":
        context["variables"][item[1]] = evaluate(parse_expression(item[2]), context)
    elif kind == "include":
        sub_context = {"root": evaluate(item[2], context), "variables": {}, "includes": context["includes"]}
        sub_output = []
        evaluate_nodes(context["includes"][item[1]], sub_context, sub_output)
        output.append("".join(sub_output))
    elif kind == "if":
        branch = item[2] if is_truthy(evaluate(parse_expression(item[1]), context)) else item[3]
        evaluate_nodes(branch, context, output)
    elif kind == "range":
        evaluate_range(item, context, output)
    else:
        raise ValueError(f"unknown template node: {kind!r}")


def evaluate_range(item: tuple, context: dict, output: list[str]):
    sequence = evaluate(parse_expression(item[2]), context)
    if sequence is NOVALUE or sequence is None:
        sequence = []
    if item[1] and isinstance(sequence, dict) and len(item[1]) == 2:
        elements = list(sequence.items())
    else:
        elements = sequence
    for element in elements:
        values = element if isinstance(element, tuple) else (element,)
        for name, value in zip(item[1], values):
            context["variables"][name] = value
        evaluate_nodes(item[3], context, output)


def evaluate_nodes(items: list[tuple], context: dict, output: list[str]):
    for item in items:
        evaluate_item(item, context, output)


def load_chart():
    values = yaml.safe_load((CHART_DIR / "values.yaml").read_text(encoding="utf-8"))
    chart = yaml.safe_load((CHART_DIR / "Chart.yaml").read_text(encoding="utf-8"))
    helper_body = parse_template((CHART_DIR / "templates" / "_helpers.tpl").read_text(encoding="utf-8"))
    includes = {item[1]: item[2] for item in helper_body if item[0] == "define"}
    return values, chart, includes


DEFAULT_VALUES, CHART_META, INCLUDES = load_chart()


def render_template(name: str, text: str, values: dict) -> str:
    context = {"root": {"Values": values}, "variables": {}, "includes": INCLUDES}
    output = []
    evaluate_nodes(parse_template(text), context, output)
    return "".join(output)


def deep_merge(base: dict, overrides: dict) -> dict:
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def render_chart(overrides: dict | None = None) -> list[dict]:
    """Render every chart template and return the parsed yaml documents.

    The documents are split on the ``\n---`` separator, the way the
    kubernetes yaml reader does: a ``---`` at the start of a template is a
    yaml document start marker, and a ``---`` glued to the following line
    still separates the documents.
    """
    values = deep_merge(DEFAULT_VALUES, overrides) if overrides else DEFAULT_VALUES
    documents = []
    for template in sorted((CHART_DIR / "templates").glob("*.yaml")):
        rendered = render_template(template.name, template.read_text(encoding="utf-8"), values)
        for chunk in rendered.split("\n---"):
            if chunk.strip():
                document = yaml.safe_load(chunk)
                if document is not None:
                    documents.append(document)
    return documents


def documents_of_kind(documents: list[dict], kind: str, name: str | None = None) -> list[dict]:
    """The rendered documents of one kind, optionally restricted to one name."""
    return [
        document
        for document in documents
        if document.get("kind") == kind and (name is None or document.get("metadata", {}).get("name") == name)
    ]


def settings_environment_variables() -> set[str]:
    """The environment variable names the application settings models read.

    Computed the way pydantic-settings resolves them: the model's
    ``env_prefix`` plus the upper-cased field name, over every settings
    module under assistant/src/assistant/impl/settings.
    """
    models = (
        APISetttings,
        InformationSettings,
        MCPSettings,
        OpenAISetttings,
        PromptSettings,
        SubagentSettings,
    )
    variables = set()
    for model in models:
        prefix = model.model_config.get("env_prefix", "")
        variables.update(prefix + field.upper() for field in model.model_fields)
    return variables


def test_chart_deploys_assistant():
    """Implements "the chart deploys the assistant" (requirements/helm-deployment.feature)

    Rendering the chart produces a deployment named ``assistant`` whose
    container runs the chat assistant image, listens on port 8080, and pulls
    the image with the ``pull-secret``.
    """
    documents = render_chart()
    (deployment,) = documents_of_kind(documents, "Deployment", "assistant")
    spec = deployment["spec"]["template"]["spec"]
    (container,) = spec["containers"]
    assert container["image"] == "ghcr.io/melvinkl/chat_assistant/assistant:latest"
    assert {"containerPort": 8080} in container["ports"]
    assert {"name": "pull-secret"} in spec["imagePullSecrets"]


def test_service_exposes_assistant():
    """Implements "the chart exposes the assistant through a service"
    (requirements/helm-deployment.feature)

    Rendering the chart produces a cluster ip service named ``assistant``
    that exposes port 8080 inside the cluster.
    """
    documents = render_chart()
    (service,) = documents_of_kind(documents, "Service", "assistant")
    assert service["spec"]["type"] == "ClusterIP"
    assert {"port": 8080, "protocol": "TCP", "targetPort": 8080} in service["spec"]["ports"]


def test_ingress_can_be_toggled():
    """Implements "the ingress can be toggled" (requirements/helm-deployment.feature)

    With ``assistant.ingress.enabled`` set to false the chart renders no
    ingress and no certificate; with the default (enabled, host
    ``assistant.localhost``) the ingress routes the host to the assistant
    service on 8080 and a cert-manager certificate is created for the host.
    """
    disabled = render_chart({"assistant": {"ingress": {"enabled": False}}})
    assert not documents_of_kind(disabled, "Ingress")
    assert not documents_of_kind(disabled, "Certificate")

    documents = render_chart()
    (ingress,) = documents_of_kind(documents, "Ingress")
    (certificate,) = documents_of_kind(documents, "Certificate")
    host = DEFAULT_VALUES["assistant"]["ingress"]["host"]
    rule = ingress["spec"]["rules"][0]
    assert rule["host"] == host
    backend = rule["http"]["paths"][0]["backend"]["service"]
    assert backend["name"] == "assistant"
    assert backend["port"]["number"] == 8080
    assert host in ingress["spec"]["tls"][0]["hosts"]
    assert certificate["spec"]["dnsNames"] == [host]
    assert certificate["spec"]["secretName"] == ingress["spec"]["tls"][0]["secretName"]


def test_pull_secret_created_from_ghcr_credentials():
    """Implements "a pull secret is created from the ghcr credentials"
    (requirements/helm-deployment.feature)

    Given the ghcrIo username, pat and email values, rendering the chart
    creates the ``pull-secret`` dockerconfigjson secret whose decoded config
    carries the ghcr.io credentials and the base64 encoded username:pat
    auth string.
    """
    credentials = {"username": "chart-user", "pat": "chart-token", "email": "chart@example"}
    documents = render_chart({"ghcrIo": credentials})
    (secret,) = documents_of_kind(documents, "Secret", "pull-secret")
    assert secret["type"] == "kubernetes.io/dockerconfigjson"
    config = json.loads(base64.b64decode(secret["data"][".dockerconfigjson"]))
    auth = base64.b64encode(f"{credentials['username']}:{credentials['pat']}".encode("utf-8")).decode("ascii")
    ghcr = {
        "username": credentials["username"],
        "password": credentials["pat"],
        "email": credentials["email"],
        "auth": auth,
    }
    assert config == {"auths": {"ghcr.io": ghcr}}


def test_mcp_settings_rendered_into_mounted_config_map():
    """Implements "the mcp servers settings are rendered into a mounted config map"
    (requirements/helm-deployment.feature)

    Rendering the chart renders the mcpServers values as json into the
    ``assistant-mcp-cm`` config map, and the assistant deployment mounts that
    config map at /config/mcp (the mcp settings loader's default path).
    """
    documents = render_chart()
    (config_map,) = documents_of_kind(documents, "ConfigMap", "assistant-mcp-cm")
    assert json.loads(config_map["data"]["SETTINGS_MCP_SERVERS"]) == DEFAULT_VALUES["mcpServers"]
    (deployment,) = documents_of_kind(documents, "Deployment", "assistant")
    spec = deployment["spec"]["template"]["spec"]
    assert {"name": "mcp-config-volume", "configMap": {"name": "assistant-mcp-cm"}} in spec["volumes"]
    (container,) = spec["containers"]
    assert {"name": "mcp-config-volume", "mountPath": "/config/mcp"} in container["volumeMounts"]


def test_subagent_settings_rendered_into_mounted_config_map():
    """Implements "the subagent settings are rendered into a mounted config map"
    (requirements/helm-deployment.feature)

    Rendering the chart renders the subagents values as json into the
    ``assistant-subagents-cm`` config map, and the assistant deployment
    mounts that config map at /config/subagents (the subagent settings
    loader's default path).
    """
    documents = render_chart()
    (config_map,) = documents_of_kind(documents, "ConfigMap", "assistant-subagents-cm")
    assert json.loads(config_map["data"]["SETTINGS_SUBAGENTS"]) == DEFAULT_VALUES["subagents"]
    (deployment,) = documents_of_kind(documents, "Deployment", "assistant")
    spec = deployment["spec"]["template"]["spec"]
    assert {"name": "subagents-config-volume", "configMap": {"name": "assistant-subagents-cm"}} in spec["volumes"]
    (container,) = spec["containers"]
    assert {"name": "subagents-config-volume", "mountPath": "/config/subagents"} in container["volumeMounts"]


def test_openai_settings_rendered_as_secret():
    """Implements "the openai settings are rendered as a secret"
    (requirements/helm-deployment.feature)

    Given the assistant.settings.openai values, rendering the chart base64
    encodes every value into the ``assistant-secret`` under its key, and the
    assistant deployment injects that secret as environment variables.
    """
    documents = render_chart()
    (secret,) = documents_of_kind(documents, "Secret", "assistant-secret")
    openai_settings = DEFAULT_VALUES["assistant"]["settings"]["openai"]
    expected = {key: base64.b64encode(value.encode("utf-8")).decode("ascii") for key, value in openai_settings.items()}
    assert secret["data"] == expected
    (deployment,) = documents_of_kind(documents, "Deployment", "assistant")
    env_from = deployment["spec"]["template"]["spec"]["containers"][0]["envFrom"]
    assert {"secretRef": {"name": "assistant-secret"}} in env_from


def test_prompt_settings_rendered_as_environment_variables():
    """Implements "the prompt settings are rendered as environment variables"
    (requirements/helm-deployment.feature)

    Given the assistant.settings.prompt and additionalInformation values,
    rendering the chart puts the six prompt values (the four rephrasing
    prompts plus the preprocessing and postprocessing system prompts) and
    the additional information into the ``assistant-cm`` config map as
    environment variable entries, and the assistant deployment injects the
    config map.
    """
    documents = render_chart()
    (config_map,) = documents_of_kind(documents, "ConfigMap", "assistant-cm")
    settings = DEFAULT_VALUES["assistant"]["settings"]
    data = config_map["data"]
    assert data["SETTINGS_ADDITIONAL_INFORMATION"].rstrip("\n") == settings["additionalInformation"].rstrip("\n")
    for key in (
        "SETTINGS_PROMPTS_REPHRASE_QUESTION_SYSTEM_PROMPT",
        "SETTINGS_PROMPTS_REPHRASE_QUESTION_USER_PROMPT",
        "SETTINGS_PROMPTS_REPHRASE_ANSWER_SYSTEM_PROMPT",
        "SETTINGS_PROMPTS_REPHRASE_ANSWER_USER_PROMPT",
        "SETTINGS_PROMPTS_PREPROCESSING_SYSTEM_PROMPT",
        "SETTINGS_PROMPTS_POSTPROCESSING_SYSTEM_PROMPT",
    ):
        assert data[key].rstrip("\n") == settings["prompt"][key].rstrip("\n"), key
    (deployment,) = documents_of_kind(documents, "Deployment", "assistant")
    env_from = deployment["spec"]["template"]["spec"]["containers"][0]["envFrom"]
    assert {"configMapRef": {"name": "assistant-cm"}} in env_from


def test_each_mcp_server_deployment_gets_own_resources():
    """Implements "each mcp server deployment gets its own resources"
    (requirements/helm-deployment.feature)

    Given mcpServers.deployments entries with name, port, image, command,
    secrets and config, rendering the chart gives each entry its own config
    map, secret, service and deployment named after the entry, and each
    deployment injects its own config map and secret as environment
    variables.
    """
    documents = render_chart()
    for entry in DEFAULT_VALUES["mcpServers"]["deployments"]:
        name = entry["name"]
        (config_map,) = documents_of_kind(documents, "ConfigMap", name)
        (secret,) = documents_of_kind(documents, "Secret", name)
        (service,) = documents_of_kind(documents, "Service", name)
        (deployment,) = documents_of_kind(documents, "Deployment", name)
        assert (config_map.get("data") or {}) == entry["config"]
        assert secret["data"] == {
            key: base64.b64encode(value.encode("utf-8")).decode("ascii") for key, value in entry["secrets"].items()
        }
        assert {"port": entry["port"], "protocol": "TCP", "targetPort": entry["port"]} in service["spec"]["ports"]
        spec = deployment["spec"]["template"]["spec"]
        (container,) = spec["containers"]
        assert container["image"] == entry["image"]
        assert entry["port"] in [port["containerPort"] for port in container["ports"]]
        if entry.get("command"):
            assert container["command"] == entry["command"]
        env_from = container["envFrom"]
        assert {"configMapRef": {"name": name}} in env_from
        assert {"secretRef": {"name": name}} in env_from


def test_default_assistant_egress_allows_only_internal_networks():
    """Implements "the default assistant egress policy allows only the internal networks"
    (requirements/helm-deployment.feature)

    With the default assistant egress values, rendering the chart renders an
    egress network policy for the assistant pods that allows exactly the
    internal network cidrs 10.0.0.0/8, 172.16.0.0/12 and 192.168.0.0/16
    and carries no allow-all rule.
    """
    documents = render_chart()
    (policy,) = documents_of_kind(documents, "NetworkPolicy", "assistant-egress")
    assert policy["spec"]["podSelector"]["matchLabels"] == {"app": "assistant"}
    assert "Egress" in policy["spec"]["policyTypes"]
    egress = policy["spec"]["egress"]
    allowed = {rule["to"][0]["ipBlock"]["cidr"] for rule in egress if "to" in rule}
    assert allowed == {"10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"}
    assert all("to" in rule for rule in egress)


def test_mcp_server_egress_disabled_by_default():
    """Implements "mcp server deployments are egress disabled by default"
    (requirements/helm-deployment.feature)

    With the default mcp server deployment values (egress enabled: false),
    the rendered chart allows no egress traffic for the mcp server pods:
    kubernetes allows all egress for a pod that no network policy selects,
    so the scenario requires a rendered egress policy for each mcp server
    pod that carries the Egress policy type without any egress rule. The
    mcp server templates render that policy unconditionally — an egress
    disabled server gets the policy without egress rules, which kubernetes
    reads as deny-all egress.
    """
    documents = render_chart()
    for entry in DEFAULT_VALUES["mcpServers"]["deployments"]:
        matching = [
            document
            for document in documents
            if document.get("kind") == "NetworkPolicy"
            and document.get("spec", {}).get("podSelector", {}).get("matchLabels", {}).get("app") == entry["name"]
        ]
        assert matching, f"no rendered network policy selects the {entry['name']} mcp server pods"
        denying = [
            policy
            for policy in matching
            if "Egress" in policy["spec"]["policyTypes"]
            and all(rule == {} or "to" not in rule for rule in (policy["spec"].get("egress") or []))
        ]
        assert denying, f"no rendered policy denies egress for the {entry['name']} mcp server pods"


def test_enabled_egress_without_allowed_hosts_allows_all():
    """Implements "an enabled egress without allowed hosts allows all egress"
    (requirements/helm-deployment.feature)

    An egress policy that is enabled with an empty allowed hosts list renders
    a network policy whose egress rule is empty, which kubernetes reads as
    allowing all egress.
    """
    documents = render_chart({"assistant": {"egress": {"enabled": True, "allowedHosts": []}}})
    (policy,) = documents_of_kind(documents, "NetworkPolicy", "assistant-egress")
    assert policy["spec"]["egress"] == [{}]


def test_ollama_subchart_enabled_by_default():
    """Implements "the ollama subchart is enabled by default"
    (requirements/helm-deployment.feature)

    The chart declares the ollama subchart as a dependency conditional on
    ``ollama.enabled``, the default values enable it, and the configured LLM
    model is listed for pulling into ollama.
    """
    dependencies = {dependency["name"]: dependency for dependency in CHART_META["dependencies"]}
    assert "ollama" in dependencies
    assert dependencies["ollama"]["condition"] == "ollama.enabled"
    assert DEFAULT_VALUES["ollama"]["enabled"] is True
    model = DEFAULT_VALUES["assistant"]["settings"]["openai"]["SETTINGS_OPENAI_MODEL"]
    assert model in DEFAULT_VALUES["ollama"]["ollama"]["models"]["pull"]


def test_rendered_assistant_environment_matches_application_settings():
    """Implements "the rendered assistant environment matches the settings the application reads"
    (requirements/helm-deployment.feature)

    Rendering the chart with the default values, every environment variable
    key the rendered chart injects into the assistant pod (the
    ``assistant-cm`` data keys plus the ``assistant-secret`` data keys, per
    the deployment's envFrom) must be an environment variable one of the
    application settings models reads.
    """
    documents = render_chart()
    (deployment,) = documents_of_kind(documents, "Deployment", "assistant")
    rendered = set()
    for reference in deployment["spec"]["template"]["spec"]["containers"][0]["envFrom"]:
        if "configMapRef" in reference:
            (config_map,) = documents_of_kind(documents, "ConfigMap", reference["configMapRef"]["name"])
            rendered.update(config_map["data"])
        if "secretRef" in reference:
            (secret,) = documents_of_kind(documents, "Secret", reference["secretRef"]["name"])
            rendered.update(secret["data"])
    read = settings_environment_variables()
    assert rendered <= read, f"rendered environment keys no settings model reads: {sorted(rendered - read)}"


def test_default_values_contain_only_consumed_keys():
    """Implements "the default values contain only keys consumed by the chart templates"
    (requirements/helm-deployment.feature)

    Reading the default values file, every top-level key must have a
    consuming chart template: either a template (including the _helpers.tpl
    helper definitions) references the key, or the key names a subchart the
    Chart.yaml declares as a dependency.
    """
    subchart_names = {dependency["name"] for dependency in CHART_META.get("dependencies", [])}
    referenced = set()
    for template in (CHART_DIR / "templates").glob("*"):
        referenced.update(re.findall(r"\.Values\.(\w+)", template.read_text(encoding="utf-8")))
    unconsumed = sorted(set(DEFAULT_VALUES) - referenced - subchart_names)
    assert not unconsumed, f"top level values keys no chart template consumes: {unconsumed}"
