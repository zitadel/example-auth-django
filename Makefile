.PHONY: start

start:
	uv sync --group dev
	uv run python manage.py migrate
	uv run python manage.py runserver localhost:3000
