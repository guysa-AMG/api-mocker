import pytest
import time
# Assumes your class and methods match this signature:
# engine = EphemeralMockEngine()
# engine.register_spec(project_id: str, spec_dict: dict) -> None
# engine.handle_request(project_id: str, http_method: str, path: str, body: dict = None) -> tuple[int, dict]
from src.api_mocker.service.mock_engine import MockEngine as EphemeralMockEngine

PROJECT_ID = "proj_local_99"


@pytest.fixture
def mock_engine():
    """Provides a fresh instance of your engine for each test."""
    return EphemeralMockEngine()


@pytest.fixture
def sample_spec():
    """OpenAPI specification fixture against which your engine will be tested."""
    return {
        "paths": {
            "/users": {
                "get": {
                    "x-latency-ms": 0,
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "example": [{"id": "u_1", "name": "Alice"}]
                                }
                            }
                        }
                    }
                },
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "age": {"type": "integer", "minimum": 18}
                                    },
                                    "required": ["name", "age"]
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "Created"}}
                }
            },
            "/orders": {
                "get": {
                    "x-latency-ms": 250,  # 250ms delay
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "example": {"status": "shipped"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }


def test_spec_registration_stores_routes(mock_engine, sample_spec):
    """Spec registration should store path mappings."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)

    # Route key convention: PROJECT_ID#METHOD#PATH
    route_key = f"{PROJECT_ID}#GET#/users"
    assert hasattr(mock_engine, "routes"), "Engine must have a 'routes' attribute"
    assert route_key in mock_engine.routes


def test_get_request_returns_example_data(mock_engine, sample_spec):
    """GET request to a defined path returns 200 and example JSON payload."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    status_code, body = mock_engine.handle_request(PROJECT_ID, "GET", "/users")

    assert status_code == 200
    assert body == [{"id": "u_1", "name": "Alice"}]


def test_unregistered_route_returns_404(mock_engine, sample_spec):
    """Unregistered paths must respond with HTTP 404."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    status_code, body = mock_engine.handle_request(PROJECT_ID, "GET", "/not-found")

    assert status_code == 404
    assert isinstance(body, dict)
    assert "error" in body


def test_post_valid_payload_creates_dynamic_state(mock_engine, sample_spec):
    """POST request should persist record and make it accessible via GET /resource/{id}."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)

    # 1. Create via POST
    post_payload = {"name": "Bob", "age": 22}
    status_code, created_data = mock_engine.handle_request(
        PROJECT_ID, "POST", "/users", body=post_payload
    )

    assert status_code == 201
    assert created_data["name"] == "Bob"
    assert "id" in created_data, "Created entity must have an generated 'id'"

    # 2. Fetch created entity via GET /users/<id>
    entity_id = created_data["id"]
    get_status, fetched_data = mock_engine.handle_request(
        PROJECT_ID, "GET", f"/users/{entity_id}"
    )

    assert get_status == 200
    assert fetched_data["name"] == "Bob"
    assert fetched_data["age"] == 22


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"name": "Charlie", "age": 16},  # Violates minimum constraint (>= 18)
        {"age": 25},                     # Missing required property ('name')
    ]
)
def test_post_schema_validation_failures(mock_engine, sample_spec, invalid_payload):
    """POST with schema-violating payload must return 400 Bad Request."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)

    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "POST", "/users", body=invalid_payload
    )

    assert status_code == 400
    assert "error" in body


def test_latency_simulation_calls_sleep(mock_engine, sample_spec, monkeypatch):
    """Routes with 'x-latency-ms' must introduce a delay via time.sleep."""
    sleep_calls = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleep_calls.append(seconds))

    mock_engine.register_spec(PROJECT_ID, sample_spec)
    status_code, _ = mock_engine.handle_request(PROJECT_ID, "GET", "/orders")

    assert status_code == 200
    assert len(sleep_calls) == 1
    assert sleep_calls[0] == 0.25  # 250ms converted to seconds