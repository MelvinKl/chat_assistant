# Task: Switch to uv

Task Number: 199
Branch: ai/issue-199-switch-to-uv

## Required Task

Switch from the package manager poetry to the package manager uv

## Steps

- [x] 1. Install uv and verify it's available in the PATH.
  - Acceptance Criteria:
    - `uv --version` shows a valid version.
    - uv is installed globally or in the user's PATH.

- [ ] 2. Update the Makefile to replace poetry commands with uv equivalents (using uv 0.10.0) and ensure dev dependencies are installed for linting and formatting.
  - Acceptance Criteria:
    - The `format`, `lint`, and `test` targets use `uv run` instead of `poetry run`.
    - The `format` and `lint` targets install dev dependencies via `uv sync --dev` before running the commands.
    - The Makefile still executes the same commands (isort, black, flake8, pytest) via uv.

- [x] 3. Update the assistant/Dockerfile to use uv (version 0.10.0) for dependency installation and application execution.
  - Acceptance Criteria:
    - Remove poetry installation and configuration steps.
    - Use `uv sync` or `uv pip install` to install dependencies.
    - Use `uv run` instead of `poetry run` to execute the application (uvicorn).
    - The Dockerfile builds successfully.

- [x] 4. Update the components/home-assistant/Dockerfile to use uv (version 0.10.0) similarly.
  - Acceptance Criteria:
    - Remove poetry installation and configuration steps.
    - Install uv via `pip install uv==0.10.0`.
    - Install dependencies using `if [ "$DEV" = 1 ] ; then uv sync --dev ; else uv sync ; fi`.
    - Adjust PATH and copying steps to account for `.venv` created by `uv` (e.g., `ENV PATH="/app/home-assistant/.venv/bin:$PATH"` and copying `/app/home-assistant/.venv` from the build stage).
    - Use `uv run` instead of `poetry run` to execute the application (uvicorn).
    - The Dockerfile builds successfully.

- [x] 5. Update other files referencing poetry (workflows, renovate, helm, README) to use uv 0.10.0.
  - Acceptance Criteria:
    - .github/workflows/test-and-lint.yml uses uv instead of poetry (removing poetry installation steps, installing uv via `pip install uv==0.10.0`, replacing `poetry install` with `uv sync --dev` to account for `.venv` creation, and replacing `poetry run` with `uv run` where applicable).
    - .github/renovate.json is updated for uv.
    - Helm values.yaml and templates update poetry references to uv (replacing `poetry run` with `uv run` where applicable).
    - README.md updates any poetry-specific instructions to uv (removing poetry installation steps, installing uv via `pip install uv==0.10.0`, replacing `poetry install` with `uv sync` or `uv sync --dev`, and `poetry run` with `uv run` where applicable).

- [x] 6. Convert poetry.lock files to uv.lock and remove poetry.lock using uv 0.10.0.
  - Acceptance Criteria:
    - Install uv via `pip install uv==0.10.0`.
    - Run `uv lock` in assistant/ and components/home-assistant/ directories (or use `uv sync --dev` to account for `.venv` creation).
    - Generated uv.lock files are present.
    - Original poetry.lock files are removed.

- [x] 7. Run `make test` and confirm it succeeds using uv 0.10.0.
  - Acceptance Criteria:
    - Ensure dependencies are installed using `uv sync --dev` to account for `.venv` creation.
    - `make test` exits successfully with no errors (confirming the Makefile's new `uv run pytest .` works, replacing `poetry run` with `uv run` where applicable).
    - All linting and tests pass (confirming the new `uv run` commands for flake8, etc. work).
