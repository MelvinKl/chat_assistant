"""Tests for the local development environment.

The repository's local development tooling lives outside the python package:
the k3d bootstrap script and cluster config under ``infrastructure/local/``,
the ``Tiltfile``, the devcontainer, the ``Makefile`` and the CI workflows.
These tests therefore inspect the artifacts statically: the Tiltfile is
parsed as python and walked with ``ast`` (its extension functions are
provided by tilt at run time, so the file is not executed), the workflows
and the k3d config are parsed as yaml, the devcontainer file is parsed as
json with its comments and trailing commas removed, and the ``Makefile``
targets are read as text.

Each test implements one scenario of requirements/local-development.feature.
"""

import ast
import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

K3D_CONFIG = REPO_ROOT / "infrastructure" / "local" / "k3d-cluster-config.yaml"
CREATE_LOCAL_ENV = REPO_ROOT / "infrastructure" / "local" / "create_local_env.sh"
TILTFILE = REPO_ROOT / "Tiltfile"
HELM_VALUES = REPO_ROOT / "infrastructure" / "helm" / "values.yaml"
ASSISTANT_DEPLOYMENT_TEMPLATE = REPO_ROOT / "infrastructure" / "helm" / "templates" / "assistant-deployment.yaml"
MAKEFILE = REPO_ROOT / "Makefile"
TEST_AND_LINT_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "test-and-lint.yml"
DOCKER_IMAGE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "docker-image.yml"
DEVCONTAINER = REPO_ROOT / ".devcontainer" / "devcontainer.json"

TILT_TREE = ast.parse(TILTFILE.read_text(encoding="utf-8"))


def tilt_calls(name: str) -> list[ast.Call]:
    """The calls to one tilt extension function in the Tiltfile."""
    return [
        node
        for node in ast.walk(TILT_TREE)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
    ]


def tilt_keyword(call: ast.Call, name: str):
    """The value of one keyword argument of a tilt extension call."""
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    raise AssertionError(f"no {name} keyword on the call to {call.func.id}")


def tilt_values() -> list[ast.expr]:
    """The elements of the helm values list the Tiltfile assembles."""
    for node in ast.walk(TILT_TREE):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "values"
            and isinstance(node.value, ast.List)
        ):
            return node.value.elts
    raise AssertionError("the Tiltfile assigns no values list")


def guarded_by_env_var(node: ast.If, var: str) -> bool:
    """Whether the If statement guards on os.environ.get(var, ...) being set."""
    test = node.test
    return (
        isinstance(test, ast.Call)
        and "os.environ.get" in ast.unparse(test)
        and bool(test.args)
        and isinstance(test.args[0], ast.Constant)
        and test.args[0].value == var
    )


def values_append_arguments(call: ast.expr) -> list[ast.expr]:
    """The arguments of a values.append(...) call, else an empty list."""
    if (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "append"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "values"
    ):
        return list(call.args)
    return []


def env_guarded_appends(var: str) -> list[ast.expr]:
    """The arguments of every values.append under the guard for one env var."""
    arguments = []
    for node in ast.walk(TILT_TREE):
        if isinstance(node, ast.If) and guarded_by_env_var(node, var):
            for statement in node.body:
                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    arguments.extend(values_append_arguments(statement.value))
    return arguments


def workflow_triggers(workflow: dict) -> dict:
    """The workflow's trigger list (yaml 1.1 reads the bare on key as true)."""
    return workflow.get(True, workflow.get("on", {}))


def workflow_run_scripts(workflow: dict) -> dict[str, str]:
    """The run scripts of the workflow's steps, keyed by step name."""
    scripts = {}
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            if "name" in step and "run" in step:
                scripts[step["name"]] = step["run"]
    return scripts


def devcontainer_spec() -> dict:
    """The devcontainer spec, minus its jsonc comments and trailing commas."""
    lines = [
        line for line in DEVCONTAINER.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("//")
    ]
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "\n".join(lines)))


def make_targets() -> dict[str, tuple[str, list[str]]]:
    """The make targets as (prerequisites, recipe lines) pairs."""
    targets: dict[str, tuple[str, list[str]]] = {}
    current = None
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("\t"):
            if current is not None:
                targets[current][1].append(line.lstrip("\t").strip())
        elif line.strip():
            name, separator, prerequisites = line.partition(":")
            if separator:
                current = name.strip()
                targets[current] = (prerequisites.strip(), [])
            else:
                current = None
    return targets


def test_local_env_script_creates_local_k3d_cluster():
    """Implements "the local env script creates a local k3d cluster" (requirements/local-development.feature)

    The bootstrap script creates the k3d cluster from
    ``k3d-cluster-config.yaml``, waits for all cluster nodes to report ready,
    and installs the bitnami nginx ingress controller (pinned to 10.3.0).
    The config file describes the topology the scenario expects: exactly one
    server node and a local image registry.
    """
    config = yaml.safe_load(K3D_CONFIG.read_text(encoding="utf-8"))
    script = CREATE_LOCAL_ENV.read_text(encoding="utf-8")
    assert config["servers"] == 1
    assert config["registries"]["create"]["name"] == "registry.localhost"
    assert "k3d cluster create" in script
    assert "--config k3d-cluster-config.yaml" in script
    assert "kubectl wait --for=condition=ready node --all" in script
    assert "helm install nginx-ingress-controller bitnami/nginx-ingress-controller" in script
    assert '--version "10.3.0"' in script


def test_tilt_builds_assistant_image_with_live_updates():
    """Implements "tilt builds the assistant image with live updates" (requirements/local-development.feature)

    The Tiltfile docker_builds the assistant image (the one the chart
    deploys) from ``assistant/Dockerfile`` and declares a live-update sync
    of ``assistant/`` into ``/app/assistant``, so source changes are synced
    into the running container.
    """
    (build,) = tilt_calls("docker_build")
    assert build.args[0].value == "ghcr.io/melvinkl/chat_assistant/assistant:latest"
    assert tilt_keyword(build, "dockerfile").value == "assistant/Dockerfile"
    live_update = tilt_keyword(build, "live_update")
    assert isinstance(live_update, ast.List)
    assert len(live_update.elts) == 1
    (sync,) = live_update.elts
    assert isinstance(sync, ast.Call)
    assert isinstance(sync.func, ast.Name)
    assert sync.func.id == "sync"
    assert [argument.value for argument in sync.args] == ["assistant", "/app/assistant"]


def test_tilt_disables_ingress_for_local_development():
    """Implements "tilt disables the ingress for local development" (requirements/local-development.feature)

    The values the Tiltfile assembles set
    ``assistant.ingress.enabled=false``, and they are applied to the
    ``assistant`` helm release deployed from ``infrastructure/helm``.
    """
    (release,) = tilt_calls("helm")
    assert release.args[0].value == "infrastructure/helm"
    assert tilt_keyword(release, "name").value == "assistant"
    set_values = tilt_keyword(release, "set")
    assert isinstance(set_values, ast.Name)
    assert set_values.id == "values"
    constants = [elt.value for elt in tilt_values() if isinstance(elt, ast.Constant)]
    assert "assistant.ingress.enabled=false" in constants


def test_debug_mode_waits_for_the_debugger():
    """Implements "in debug mode the assistant waits for the debugger" (requirements/local-development.feature)

    The Tiltfile defines the ``debug`` flag; when it is enabled, the release
    values carry ``assistant.debug=true`` (and the image is built with the
    DEV build argument) and the chart deployment template then runs the
    container with the chart's ``debugArgs``: debugpy listening on
    ``0.0.0.0:5679`` with ``--wait-for-client``, before uvicorn starts.
    """
    defined_bools = [
        argument.value
        for node in ast.walk(TILT_TREE)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "define_bool"
        for argument in node.args
        if isinstance(argument, ast.Constant)
    ]
    assert "debug" in defined_bools
    formatted = [
        elt.left.value for elt in tilt_values() if isinstance(elt, ast.BinOp) and isinstance(elt.left, ast.Constant)
    ]
    assert "assistant.debug=%s" in formatted
    values = yaml.safe_load(HELM_VALUES.read_text(encoding="utf-8"))
    debug_args = values["assistant"]["debugArgs"]
    assert "debugpy" in debug_args
    assert "--listen" in debug_args
    assert "0.0.0.0:5679" in debug_args
    assert "--wait-for-client" in debug_args
    template = ASSISTANT_DEPLOYMENT_TEMPLATE.read_text(encoding="utf-8")
    assert "if .Values.assistant.debug" in template
    assert "debugArgs" in template


def test_tilt_forwards_the_api_and_debugger_ports():
    """Implements "tilt forwards the api and debugger ports" (requirements/local-development.feature)

    The Tiltfile attaches port forwards to the assistant resource: 8080 is
    forwarded for the assistant api (linked at /docs) and 5679 for the
    debugger.
    """
    (resource,) = tilt_calls("k8s_resource")
    assert resource.args[0].value == "assistant"
    forwards = tilt_keyword(resource, "port_forwards")
    assert isinstance(forwards, ast.List)
    (port_forward,) = [
        elt
        for elt in forwards.elts
        if isinstance(elt, ast.Call) and isinstance(elt.func, ast.Name) and elt.func.id == "port_forward"
    ]
    assert [argument.value for argument in port_forward.args] == [8080, 8080]
    assert tilt_keyword(port_forward, "link_path").value == "/docs"
    strings = [elt.value for elt in forwards.elts if isinstance(elt, ast.Constant)]
    assert "5679:5679" in strings


def test_custom_llm_disables_local_ollama_deployment():
    """Implements "a custom LLM disables the local ollama deployment" (requirements/local-development.feature)

    When a custom ``SETTINGS_OPENAI_BASE_URL`` is set in the environment,
    the Tiltfile appends the value to the release's openai settings and
    appends ``ollama.enabled=false``, which disables the ollama subchart of
    the assistant helm release.
    """
    arguments = env_guarded_appends("SETTINGS_OPENAI_BASE_URL")
    unparsed = [ast.unparse(argument) for argument in arguments]
    assert "'ollama.enabled=false'" in unparsed
    assert any("SETTINGS_OPENAI_BASE_URL=" in script for script in unparsed)


def test_makefile_exposes_format_lint_and_test_targets():
    """Implements "the makefile exposes format, lint and test targets" (requirements/local-development.feature)

    The ``format`` target applies isort and black inside the assistant
    project, the ``lint`` target runs flake8 there, and the ``test`` target
    depends on ``lint`` and then runs the pytest suite — everything through
    ``uv`` from the assistant directory.
    """
    targets = make_targets()
    format_recipe = " ".join(targets["format"][1])
    assert "cd assistant" in format_recipe
    assert "uv run --extra dev isort ." in format_recipe
    assert "uv run --extra dev black ." in format_recipe
    lint_recipe = " ".join(targets["lint"][1])
    assert "cd assistant" in lint_recipe
    assert "uv run --extra dev flake8" in lint_recipe
    prerequisites, test_recipe = targets["test"]
    assert prerequisites == "lint"
    assert " ".join(test_recipe) == "cd assistant; uv run --extra dev pytest ."


def test_ci_test_and_lint_job_validates_pull_requests():
    """Implements "the CI test and lint job validates pull requests" (requirements/local-development.feature)

    The ``test-and-lint.yml`` workflow runs on pull requests targeting
    ``main``: it installs the dependencies with ``uv sync`` inside the
    assistant project, then runs the ``make lint`` and ``make test``
    targets.
    """
    workflow = yaml.safe_load(TEST_AND_LINT_WORKFLOW.read_text(encoding="utf-8"))
    assert workflow_triggers(workflow)["pull_request"]["branches"] == ["main"]
    scripts = workflow_run_scripts(workflow)
    assert "uv sync --extra dev" in scripts["Install dependencies"]
    assert scripts["Lint"].strip() == "make lint"
    assert scripts["Test with pytest"].strip() == "make test"


def test_ci_docker_image_job_publishes_release_images():
    """Implements "the CI docker image job publishes release images" (requirements/local-development.feature)

    The ``docker-image.yml`` workflow triggers on ``release: published``: it
    builds the assistant image from ``assistant/Dockerfile`` tagged with the
    release tag name, pushes it to ghcr.io, and re-tags and pushes the same
    image as ``latest``.
    """
    workflow = yaml.safe_load(DOCKER_IMAGE_WORKFLOW.read_text(encoding="utf-8"))
    assert workflow_triggers(workflow)["release"]["types"] == ["published"]
    build_step = [
        step for step in workflow["jobs"]["build"]["steps"] if step.get("name") == "Build and push Docker image"
    ][0]
    script = build_step["run"]
    assert "docker build . -f assistant/Dockerfile -t $TAG" in script
    assert "${{ github.event.release.tag_name }}" in script
    assert "docker push $TAG" in script
    assert "docker image tag $TAG $LATEST_TAG" in script
    assert "docker push $LATEST_TAG" in script
    assert ":latest" in script


def test_devcontainer_provides_development_tooling():
    """Implements "the devcontainer provides the development tooling" (requirements/local-development.feature)

    The devcontainer runs a python 3.13 image and installs the development
    tooling as devcontainer features: docker outside of docker, kubectl,
    helm and minikube, and tilt.
    """
    spec = devcontainer_spec()
    assert spec["image"] == "mcr.microsoft.com/devcontainers/python:3.13-bookworm"
    features = spec["features"]
    assert any("docker" in name for name in features)
    assert any("kubectl-helm" in name for name in features)
    assert any("tilt" in name for name in features)
