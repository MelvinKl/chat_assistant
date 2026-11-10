"""Guard that keeps the pytest oracle aligned with the Gherkin requirements.

The test suite and the oracle extracted into ``requirements/`` join on a
scenario reference. Every test that implements an extracted scenario cites
the scenario it arose from in its docstring; two machine forms are accepted:

    Implements "the health check repeats on a five minute interval"
    (requirements/health-api.feature)

    requirements/health-api.feature::the health check repeats on a five
    minute interval

A test that implements several scenarios cites each of them, one citation per
line, in the first form. A test that only serves correctness carries no such
citation, and the Gherkin text itself stays in the feature files, which
remain the single source of truth: tests never duplicate Given/When/Then
lines, they only cite the scenario title they implement.

The guard verifies the alignment in both directions (the mechanism of AC1 in
plans/11.md, backing AC2-AC15):

* every ``Scenario:`` title extracted from ``requirements/*.feature`` is
  referenced by at least one test. The guard is parametrised per feature
  file, so it turns green per area as the referencing tests of the brownfield
  alignment plan land, step by step, and is fully green once the whole plan
  has landed;
* no test references a scenario that is absent from ``requirements/``.
"""

import ast
import re
from collections import defaultdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / "requirements"
TESTS_DIR = Path(__file__).resolve().parent

# A quoted scenario title directly followed by its feature file.
REFERENCE_WITH_FILE = re.compile(r'"(?P<title>[^"\n]+)"\s*\(\s*(?P<file>requirements/[\w-]+\.feature)\s*\)')
# The machine form <feature file>::<scenario name>.
REFERENCE_WITH_SEPARATOR = re.compile(r"(?P<file>requirements/[\w-]+\.feature)::(?P<title>.+)")


def extract_scenario_titles(feature_file: Path) -> list[str]:
    """Return the verbatim Scenario: titles of one feature file, in file order."""
    titles = []
    for line in feature_file.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("Scenario:"):
            titles.append(line.strip().split(":", 1)[1].strip())
    return titles


EXTRACTED_SCENARIOS: dict[str, list[str]] = {
    feature_file.relative_to(REPO_ROOT).as_posix(): extract_scenario_titles(feature_file)
    for feature_file in sorted(REQUIREMENTS_DIR.glob("*.feature"))
}


def docstrings_of_test_functions(module: Path) -> list[tuple[str, str]]:
    """Return (test name, docstring) for every test function of one test module."""
    tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
    return [
        (node.name, ast.get_docstring(node) or "")
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]


def find_references(docstring: str) -> set[tuple[str, str]]:
    """Return the (feature file, scenario title) pairs cited in one docstring."""
    references = {(match["file"], match["title"].strip()) for match in REFERENCE_WITH_FILE.finditer(docstring)}
    references |= {(match["file"], match["title"].strip()) for match in REFERENCE_WITH_SEPARATOR.finditer(docstring)}
    return references


def collect_suite_references() -> dict[tuple[str, str], list[str]]:
    """Scan every test module for scenario references in test docstrings."""
    references: dict[tuple[str, str], list[str]] = defaultdict(list)
    for module in sorted(TESTS_DIR.rglob("*.py")):
        for test_name, docstring in docstrings_of_test_functions(module):
            for reference in find_references(docstring):
                location = "tests/" + str(module.relative_to(TESTS_DIR).with_suffix("")) + "::" + test_name
                references[reference].append(location)
    return references


SUITE_REFERENCES = collect_suite_references()


@pytest.mark.parametrize("feature_file", sorted(EXTRACTED_SCENARIOS))
def test_feature_file_scenarios_are_referenced(feature_file: str):
    """Every scenario of one feature file is referenced by at least one test.

    Parametrised per feature file, so the guard turns green per area as the
    referencing tests of the brownfield alignment plan land, step by step.
    """
    referenced = set(SUITE_REFERENCES)
    missing = [title for title in EXTRACTED_SCENARIOS[feature_file] if (feature_file, title) not in referenced]
    message = "; ".join(missing)
    assert not missing, f"Scenarios of {feature_file} no test references: {message}"


def test_no_test_references_a_missing_scenario():
    """Every reference in the suite resolves to a scenario extracted from requirements/.

    A reference names the scenario's feature file, so it must resolve to a
    Scenario: title that the very file carries; anything else is a dangling
    reference and fails the guard.
    """
    extracted = {(file, title) for file, titles in EXTRACTED_SCENARIOS.items() for title in titles}
    dangling = sorted(f"{file}::{title}" for (file, title) in SUITE_REFERENCES if (file, title) not in extracted)
    message = "; ".join(dangling)
    assert not dangling, f"Scenario references that do not resolve to requirements/: {message}"
