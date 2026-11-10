# The test entry points run under uv. A runner without uv installs it from
# the official standalone installer (which needs no pre-installed python —
# uv brings its own python for `uv sync`); the CI test job installs the same
# tool the other way (.github/workflows/test-and-lint.yml). The install lands
# in ~/.local/bin, which the recipes below pick up from the PATH.
export PATH := $(HOME)/.local/bin:$(PATH)

format: ensure-uv
	cd assistant; uv sync --dev; uv run --extra dev isort .; uv run --extra dev black .

lint: ensure-uv
	cd assistant; uv sync --dev; uv run --extra dev flake8

test: lint
	cd assistant; uv run --extra dev pytest .

ensure-uv:
	@command -v uv >/dev/null 2>&1 && exit 0
	@{ curl -LsSf https://astral.sh/uv/install.sh 2>/dev/null | sh || { command -v wget >/dev/null 2>&1 && wget -qO- https://astral.sh/uv/install.sh | sh; } || { echo "error: uv is missing and could not be installed" >&2; exit 127; }; }
	@command -v uv >/dev/null 2>&1
