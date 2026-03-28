format:
	cd assistant; uv sync --dev; uv run --extra dev isort .; uv run --extra dev black .

lint:
	cd assistant; uv sync --dev; uv run --extra dev flake8

test: lint
	cd assistant; uv run --extra dev pytest .
