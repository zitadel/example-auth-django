.PHONY: start

start:
	poetry install
	poetry run python manage.py migrate
	poetry run python manage.py runserver localhost:3000
