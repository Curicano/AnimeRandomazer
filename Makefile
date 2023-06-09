install:
	pip install poetry && \
	poetry install

start:
	poetry run python AnimeRandomazer/main.py