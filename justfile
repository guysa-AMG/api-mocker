check-lint:
	uv run ruff --check src/
run-test:
	uv run pytest
run-dev:
    uv run fastapi dev src/api_mocker/main.py
run-prod:
    uv run fastapi run src/api_mocker/main.py
