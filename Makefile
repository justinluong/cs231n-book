run:
	poetry run python main.py

typecheck:
	poetry run mypy main.py --strict