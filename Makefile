format:
	cd assistant; uv sync --dev; uv run --extra dev isort .; uv run --extra dev black .

lint:
	cd assistant; uv sync --dev; uv run --extra dev flake8

test: lint test-e2e
	cd assistant; uv run --extra dev pytest .

test-e2e:
	./test-e2e.sh
