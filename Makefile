format:
	cd assistant; poetry run isort .; poetry run black .

lint: 
	cd assistant; poetry run flake8

test:
	cd assistant; poetry run pytest .