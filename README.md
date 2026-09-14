WTC-ZBPTTJTD 
[![Terraform](https://github.com/guysa-AMG/api-mocker/actions/workflows/terraform.yml/badge.svg)](https://github.com/guysa-AMG/api-mocker/actions/workflows/terraform.yml) [![Api Mocker](https://github.com/guysa-AMG/api-mocker/actions/workflows/api-mock.yml/badge.svg)](https://github.com/guysa-AMG/api-mocker/actions/workflows/api-mock.yml)

# API Mocker

An ephemeral API mock server for developing and testing clients against OpenAPI-style response definitions. The project includes an in-memory mock engine, a FastAPI application, an example specification, and container/deployment configuration.

## Features

- Register API specifications per project.
- Store route definitions in memory.
- Return configured response examples for mock requests.
- Keep project state isolated in the mock engine.
- Support request and response schema definitions through OpenAPI-style dictionaries.
- Simulate route latency with the `x-latency-ms` extension.
- Expose FastAPI's interactive API documentation and Scalar reference.

> **Status:** This project is under active development. The HTTP API for registering specifications and dispatching mock requests is still being wired into the FastAPI application. The engine can currently be used directly from Python.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

## Installation

Clone the repository and install its dependencies:

```bash
git clone https://github.com/guysa-AMG/api-mocker.git
cd api-mocker
uv sync
```

## Running the server

Start the development server with automatic reload:

```bash
uv run fastapi dev src/api_mocker/main.py
```

For a production-style local run:

```bash
uv run fastapi run src/api_mocker/main.py
```

The same commands are available through the `justfile`:

```bash
just run-dev
just run-prod
```

The application listens on the default FastAPI host and port. Visit `/docs` for Swagger UI or `/scalar` for the Scalar API reference.

## Using the mock engine

The engine accepts a project identifier and an OpenAPI-style specification:

```python
from src.api_mocker.service.mock_engine import MockEngine

engine = MockEngine()
engine.register_spec(
    "local-project",
    {
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "example": [{"id": 1, "name": "Jane Doe"}]
                                }
                            }
                        }
                    }
                }
            }
        }
    },
)

status_code, response_body = engine.handle_request(
    "local-project",
    "GET",
    "/users",
)
```

An example specification is available at [`src/api_mocker/data/example.yml`](src/api_mocker/data/example.yml).

## Testing and linting

Run the test suite:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check src/
```

## Docker

Build and run the container:

```bash
docker build -f dockerfile -t api-mocker .
docker run --rm -p 8000:8000 api-mocker
```

## Deployment

The [`deployment`](deployment) directory contains Terraform configuration for deploying the container image to Render. Review provider credentials, ownership, region, and image settings before applying it.

## Project layout

```text
src/api_mocker/
├── data/                  # Example mock specifications
├── interface/             # Mock engine interfaces
├── service/               # Mock engine and API service code
└── main.py                # FastAPI application
test/                      # Engine tests
deployment/                # Render/Terraform configuration
```

## Contributing

1. Create a feature branch.
2. Make focused changes and add or update tests.
3. Run `uv run pytest` and `uv run ruff check src/`.
4. Open a pull request with a clear description of the change.

## License

This project is licensed under the terms in [`LICENSE`](LICENSE).
