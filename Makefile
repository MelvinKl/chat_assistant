format:
	cd assistant; uv run isort .; uv run black .

lint: 
	cd assistant; uv run flake8

test: lint
	cd assistant; uv run pytest .
