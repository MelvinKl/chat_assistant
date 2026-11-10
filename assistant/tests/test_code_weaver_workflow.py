"""Tests for the code-weaver factory workflow.

The repository wires the code-weaver factory into its GitHub workflows to
turn labeled issues into pull requests. The workflow file is maintained by
the factory itself and the README does not document it, so the feature file
is the sole scenario source here; these tests therefore parse
``.github/workflows/code-weaver.yml`` as yaml and assert the wiring the
extracted scenarios describe: the trigger conditions, the reusable factory
job's pinned reference, its runner/budget/model inputs, and the
secrets-only credential passing.

Each test implements one scenario of requirements/code-weaver-workflow.feature.
"""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CODE_WEAVER_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "code-weaver.yml"

WORKFLOW = yaml.safe_load(CODE_WEAVER_WORKFLOW.read_text(encoding="utf-8"))

# The factory job's reusable-workflow reference: an owner and a repository,
# the workflow path, and a version tag — a moving branch ref is not a stable
# ref, so the reference may only be pinned to a tag.
PINNED_FACTORY_REFERENCE = re.compile(
    r"^(?P<owner>[\w-]+)/(?P<repo>[\w-]+)/\.github/workflows/(?P<workflow>[\w-]+\.yml)@(?P<ref>v?\d+)$"
)

# A plain input carrying a credential would defeat the secrets-only passing;
# none of these names may appear among the job's ``with`` inputs.
CREDENTIAL_INPUT = re.compile(r"token|secret|password|api[-_]?key", re.IGNORECASE)


def trigger_map() -> dict:
    """The workflow's trigger mapping (yaml 1.1 reads the bare on key as true)."""
    return WORKFLOW.get(True, WORKFLOW.get("on", {}))


def factory_job() -> dict:
    """The reusable-workflow factory job of the code-weaver workflow."""
    return WORKFLOW["jobs"]["factory"]


def test_workflow_starts_when_an_issue_is_labeled():
    """Implements "the workflow starts when an issue is labeled" (requirements/code-weaver-workflow.feature)

    The workflow's issue trigger carries only the ``labeled`` type, so a
    run starts when an issue receives a label — opening or editing an
    issue does not fire the workflow.
    """
    assert trigger_map()["issues"]["types"] == ["labeled"]


def test_workflow_can_be_started_manually():
    """Implements "the workflow can be started manually" (requirements/code-weaver-workflow.feature)

    The workflow dispatch trigger is enabled with an optional string
    ``issue_number`` input, so the workflow can be run from the GitHub UI
    for a given issue.
    """
    dispatch = trigger_map()["workflow_dispatch"]
    issue_number = dispatch["inputs"]["issue_number"]
    assert issue_number["type"] == "string"
    assert issue_number["required"] is False


def test_factory_job_references_a_pinned_factory_version():
    """Implements "the factory job references a pinned factory version" (requirements/code-weaver-workflow.feature)

    The factory job uses the reusable factory workflow of the code-weaver
    repository, and the reference pins an owner and a version tag rather
    than a moving branch ref.
    """
    uses = factory_job()["uses"]
    assert uses == "MelvinKl/code-weaver/.github/workflows/factory.yml@19"
    match = PINNED_FACTORY_REFERENCE.match(uses)
    assert match is not None
    assert match["owner"] == "MelvinKl"
    assert match["workflow"] == "factory.yml"


def test_factory_runs_on_the_configured_runner():
    """Implements "the factory runs on the configured runner" (requirements/code-weaver-workflow.feature)

    A reusable-workflow job may only carry ``uses``/``with``/``secrets``,
    so the factory job declares no runner of its own; the runner is chosen
    through the factory's ``runner`` input, set to ``self-hosted``.
    """
    job = factory_job()
    assert "runs-on" not in job
    assert job["with"]["runner"] == "self-hosted"


def test_factory_clones_its_runtime_tree_from_main():
    """Implements "the factory clones its runtime tree from main" (requirements/code-weaver-workflow.feature)

    The stage jobs clone the factory's runtime tree from the factory
    repository, so the ``factory-ref`` input is set to ``main`` — the same
    ref as the ``uses`` line.
    """
    assert factory_job()["with"]["factory-ref"] == "main"


def test_factory_loop_budget_and_timeout_are_configured():
    """Implements "the factory loop budget and timeout are configured" (requirements/code-weaver-workflow.feature)

    The factory's budget is passed through the job inputs: a job timeout
    of 2000 and a maximum loop count of 25.
    """
    job = factory_job()
    assert job["with"]["job-timeout"] == 2000
    assert job["with"]["max-loops"] == 25


def test_factory_uses_the_configured_llm_model():
    """Implements "the factory uses the configured LLM model" (requirements/code-weaver-workflow.feature)

    The ``llm-model`` input is set to ``Qwen3.8`` — the repository's one
    adjustable LLM setting.
    """
    assert factory_job()["with"]["llm-model"] == "Qwen3.8"


def test_factory_only_acts_on_requirements_labeled_issues():
    """Implements "the factory only acts on requirements labeled issues" (requirements/code-weaver-workflow.feature)

    The ``ai-requirements-label`` input is set to the repository's
    ``code-weaver`` label, so the factory picks up exactly the issues the
    workflow is triggered on.
    """
    assert factory_job()["with"]["ai-requirements-label"] == "code-weaver"


def test_credentials_are_passed_as_secrets():
    """Implements "credentials are passed as secrets" (requirements/code-weaver-workflow.feature)

    The factory job receives the gh token and the pi configuration
    (``PI_*``) through the job's ``secrets`` mapping, where every value is
    a context expression, and no credential appears among the job's plain
    inputs.
    """
    job = factory_job()
    secrets = job["secrets"]
    assert set(secrets) == {"GH_TOKEN", "PI_MODELS", "PI_SETTINGS", "PI_MCP", "PI_EXTENSION_ENV"}
    assert secrets["GH_TOKEN"] == "${{ secrets.GH_TOKEN }}"
    for name in ("PI_MODELS", "PI_SETTINGS", "PI_MCP", "PI_EXTENSION_ENV"):
        assert secrets[name].startswith("${{ vars.")
    assert not any(CREDENTIAL_INPUT.search(name) for name in job["with"])
