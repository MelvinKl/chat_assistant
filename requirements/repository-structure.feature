@repository-structure
Feature: Documentation matches the repository

  The README documents the layout, the configuration and the development setup
  of the repository, and the documentation stays in sync with the actual state.

  Scenario: the documented directory structure exists in the repository
    When the directory structure section of the README is read
    Then every directory and file it lists exists in the repository

  Scenario: the documented prompt defaults match the chart defaults
    When the prompt settings table of the README is read
    Then every documented default equals the corresponding default in the helm chart values

  Scenario: the getting started section references existing files
    When the getting started section of the README is read
    Then every repository file it references exists in the repository

  Scenario: every secret mentioned by the README is consumed by the deployment
    When the README is read
    Then every environment secret it names is consumed by the application or the helm chart

  Scenario: the repository ships the apache license
    When the repository root is read
    Then a LICENSE file with the Apache 2.0 license is present

  Scenario: the default additional information advertises the apache license
    Given the default chart values
    When the additional information default is read
    Then it states that the source code is available under the Apache2 license
