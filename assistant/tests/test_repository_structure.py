"""Tests for the consistency between the README documentation and the repository.

The README is the repository's only prose documentation. These tests read it
together with the repository tree, ``.gitignore`` and the helm chart values,
and check that what the documentation describes and what the repository
ships stay in sync. The README is parsed as markdown: a section body is the
lines between its heading and the next heading of the same or higher level,
and the backticked spans carry the documented values.

Each test implements one scenario of requirements/repository-structure.feature.
"""

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
README = REPO_ROOT / "README.md"
GITIGNORE = REPO_ROOT / ".gitignore"
CHART_VALUES = REPO_ROOT / "infrastructure" / "helm" / "values.yaml"
ASSISTANT_CM_TEMPLATE = REPO_ROOT / "infrastructure" / "helm" / "templates" / "assistant-cm.yaml"

ENVIRONMENT_VARIABLE = re.compile(r"^[A-Z][A-Z0-9_]+$")
SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSWORD")


def section_lines(heading: str) -> list[str]:
    """The lines of one README section, up to the next heading of the same or higher level."""
    lines = README.read_text(encoding="utf-8").splitlines()
    start = None
    level = 0
    end = len(lines)
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if start is None:
            if match is not None and match.group(2).strip() == heading:
                start, level = index + 1, len(match.group(1))
        elif match is not None and len(match.group(1)) <= level:
            end = index
            break
    return lines[start:end] if start is not None else []


def backticked(text: str) -> list[str]:
    """The backticked spans of one line of markdown."""
    return re.findall(r"`([^`]+)`", text)


def chart_values() -> dict:
    """The default values of the helm chart."""
    return yaml.safe_load(CHART_VALUES.read_text(encoding="utf-8"))


def listed_directory_entries() -> list[str]:
    """The directories and files the Directory Structure section lists.

    The subsection headings list the top-level entries and their bullets list
    the entries of the subsection (``home-assistant`` under ``components``),
    resolved relative to the subsection's own path.
    """
    entries: list[str] = []
    subsection: list[str] = []
    for line in section_lines("Directory Structure"):
        if line.startswith("### "):
            subsection = backticked(line)
            entries.extend(subsection)
        elif line.lstrip().startswith("*"):
            entries.extend(f"{parent}/{token}" for parent in subsection for token in backticked(line))
    return entries


def test_directory_structure_exists_in_repository():
    """Implements "the documented directory structure exists in the repository"
    (requirements/repository-structure.feature)

    Every directory and file the Directory Structure section lists must
    exist in the repository tree: the subsection heading entries
    (``assistant``, ``infrastructure/helm``,
    ``infrastructure/local/create_local_env.sh``, ``.vscode`` and
    ``.devcontainer``) and the subsection bullets — every listed entry is
    present in the tree.
    """
    missing = [entry for entry in listed_directory_entries() if not (REPO_ROOT / entry).exists()]
    assert not missing, f"documented entries missing from the repository tree: {missing}"


def documented_prompt_defaults() -> dict[str, str]:
    """The README's Prompts table as {environment variable key: documented default}."""
    table: dict[str, str] = {}
    for line in section_lines("Prompts"):
        if not line.lstrip().startswith("|"):
            continue
        cells = line.strip().strip("|").split("|")
        if len(cells) < 2:
            continue
        key_spans = backticked(cells[0])
        default_spans = backticked(cells[1])
        if not key_spans or not default_spans:
            continue
        table[key_spans[0].rsplit(".", 1)[-1]] = default_spans[0].replace("\\n", "\n")
    return table


def test_documented_prompt_defaults_match_chart_defaults():
    """Implements "the documented prompt defaults match the chart defaults"
    (requirements/repository-structure.feature)

    Given the prompt settings table of the README, every documented default
    equals the corresponding default in the helm chart values
    (``assistant.settings.prompt``).
    """
    chart_defaults = chart_values()["assistant"]["settings"]["prompt"]
    documented = documented_prompt_defaults()
    mismatches = {
        key
        for key, default in documented.items()
        if key not in chart_defaults or chart_defaults[key].rstrip("\n") != default.rstrip("\n")
    }
    assert not mismatches, f"documented prompt defaults that differ from the chart defaults: {sorted(mismatches)}"


def gitignored_names() -> set[str]:
    """The file names the repository marks as user-local in .gitignore."""
    return {
        line.strip()
        for line in GITIGNORE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def getting_started_file_references() -> list[str]:
    """The backticked file references of the Getting Started section.

    Environment variable names are not file references (they belong to the
    secrets scenario); a file the section tells the reader to create is
    user-local, which the repository marks by listing it in .gitignore.
    """
    references: list[str] = []
    for line in section_lines("Getting Started"):
        references.extend(span for span in backticked(line) if not ENVIRONMENT_VARIABLE.match(span))
    return references


def test_getting_started_references_existing_files():
    """Implements "the getting started section references existing files"
    (requirements/repository-structure.feature)

    Every repository file the Getting Started section references must exist
    in the repository tree. The section tells the reader to create a
    ``.env`` file; that file is user-local, which the repository marks by
    listing it in ``.gitignore``, so it counts as referenced-and-known
    rather than as a shipped repository file.
    """
    gitignored = gitignored_names()
    missing = [
        reference
        for reference in getting_started_file_references()
        if not (REPO_ROOT / reference).exists() and reference not in gitignored
    ]
    assert not missing, f"Getting Started references absent from the repository tree: {missing}"


def named_environment_secrets() -> list[str]:
    """The environment secret variable names the README names.

    The backticked spans of the README whose dot-separated segments include
    an all-caps environment variable name that marks a secret (KEY, TOKEN,
    SECRET or PASSWORD in the name).
    """
    named: set[str] = set()
    for line in README.read_text(encoding="utf-8").splitlines():
        for span in backticked(line):
            for segment in span.split("."):
                if ENVIRONMENT_VARIABLE.match(segment) and SECRET_NAME.search(segment):
                    named.add(segment)
    return sorted(named)


def application_environment_variables() -> set[str]:
    """The environment variables the application's settings models read.

    Computed the way pydantic-settings resolves them: the model's
    ``env_prefix`` plus the upper-cased field name, over every settings
    module under assistant/src/assistant/impl/settings.
    """
    models = (APISetttings, InformationSettings, MCPSettings, OpenAISetttings, PromptSettings, SubagentSettings)
    return {
        model.model_config.get("env_prefix", "") + field.upper() for model in models for field in model.model_fields
    }


def chart_environment_keys() -> set[str]:
    """The environment variable keys the chart injects into the assistant pod.

    The data keys of the rendered ``assistant-cm`` config map (the
    ``SETTINGS_`` keys of the template) plus the ``assistant-secret`` data
    keys (the chart ranges the openai settings values over it).
    """
    config_map_keys = set(
        re.findall(r"^\s{2}(SETTINGS_\w+):", ASSISTANT_CM_TEMPLATE.read_text(encoding="utf-8"), re.MULTILINE)
    )
    return config_map_keys | set(chart_values()["assistant"]["settings"]["openai"])


def test_named_environment_secrets_are_consumed_by_the_deployment():
    """Implements "every secret mentioned by the README is consumed by the deployment"
    (requirements/repository-structure.feature)

    Every environment secret the README names must be consumed either by the
    application (one of the six settings models reads the variable) or by the
    deployment (the chart renders the variable into the assistant pod's
    environment). ``SETTINGS_OPENAI_API_KEY`` is the secret the README names,
    and the deployment consumes it both ways.
    """
    consumed = application_environment_variables() | chart_environment_keys()
    unconsumed = [secret for secret in named_environment_secrets() if secret not in consumed]
    assert not unconsumed, f"environment secrets the README names that no application or chart consumes: {unconsumed}"


def test_repository_ships_the_apache_license():
    """Implements "the repository ships the apache license"
    (requirements/repository-structure.feature)

    The repository root carries a LICENSE file whose text is the Apache
    License, Version 2.0.
    """
    license_file = REPO_ROOT / "LICENSE"
    assert license_file.is_file()
    text = license_file.read_text(encoding="utf-8")
    assert "Apache License" in text
    assert "Version 2.0" in text


def test_default_additional_information_advertises_the_apache_license():
    """Implements "the default additional information advertises the apache license"
    (requirements/repository-structure.feature)

    Given the default chart values, the additional information default
    (``assistant.settings.additionalInformation``) states that the source
    code is available under the Apache2 license.
    """
    information = chart_values()["assistant"]["settings"]["additionalInformation"]
    assert "source code" in information
    assert "Apache2" in information
