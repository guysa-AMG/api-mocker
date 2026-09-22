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


# ============================================================================
# Project Isolation Tests
# ============================================================================
def test_multiple_projects_isolated(mock_engine):
    """Different projects must have isolated specs and routes."""
    project_a = "proj_a"
    project_b = "proj_b"
    
    spec_a = {
        "paths": {
            "/users": {
                "get": {
                    "responses": {"200": {"content": {"application/json": {"example": {"id": "a_1"}}}}}
                }
            }
        }
    }
    spec_b = {
        "paths": {
            "/products": {
                "get": {
                    "responses": {"200": {"content": {"application/json": {"example": {"id": "b_1"}}}}}
                }
            }
        }
    }
    
    mock_engine.register_spec(project_a, spec_a)
    mock_engine.register_spec(project_b, spec_b)
    
    # Project A should have /users, not /products
    status_a, body_a = mock_engine.handle_request(project_a, "GET", "/users")
    assert status_a == 200
    
    status_a_products, _ = mock_engine.handle_request(project_a, "GET", "/products")
    assert status_a_products == 404
    
    # Project B should have /products, not /users
    status_b, body_b = mock_engine.handle_request(project_b, "GET", "/products")
    assert status_b == 200
    
    status_b_users, _ = mock_engine.handle_request(project_b, "GET", "/users")
    assert status_b_users == 404


def test_unregistered_project_returns_404(mock_engine, sample_spec):
    """Requests to an unregistered project must return 404."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    
    status_code, body = mock_engine.handle_request("unknown_project", "GET", "/users")
    assert status_code == 404
    assert isinstance(body, dict)
    assert "error" in body


# ============================================================================
# HTTP Method Tests (GET, POST, PUT, DELETE, PATCH)
# ============================================================================
@pytest.fixture
def spec_with_methods():
    """Spec with multiple HTTP methods on same path."""
    return {
        "paths": {
            "/users/{id}": {
                "get": {
                    "responses": {"200": {"content": {"application/json": {"example": {"id": "u_1", "name": "Alice"}}}}}
                },
                "put": {
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object"}}}},
                    "responses": {"200": {"description": "Updated"}}
                },
                "delete": {
                    "responses": {"204": {"description": "Deleted"}}
                },
                "patch": {
                    "requestBody": {"content": {"application/json": {"schema": {"type": "object"}}}},
                    "responses": {"200": {"description": "Patched"}}
                }
            }
        }
    }


def test_put_method_returns_correct_status(mock_engine, spec_with_methods):
    """PUT request must return appropriate response status."""
    mock_engine.register_spec(PROJECT_ID, spec_with_methods)
    
    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "PUT", "/users/123", body={"name": "Updated"}
    )
    assert status_code == 200


def test_delete_method_returns_204(mock_engine, spec_with_methods):
    """DELETE request must return 204 No Content."""
    mock_engine.register_spec(PROJECT_ID, spec_with_methods)
    
    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "DELETE", "/users/123"
    )
    assert status_code == 204


def test_patch_method_returns_correct_status(mock_engine, spec_with_methods):
    """PATCH request must return appropriate response status."""
    mock_engine.register_spec(PROJECT_ID, spec_with_methods)
    
    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "PATCH", "/users/123", body={"name": "Patched"}
    )
    assert status_code == 200


def test_unsupported_method_returns_405(mock_engine, sample_spec):
    """Unsupported HTTP method on valid path must return 405 Method Not Allowed."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    
    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "DELETE", "/users"
    )
    assert status_code == 405
    assert isinstance(body, dict)
    assert "error" in body


# ============================================================================
# Error Handling & Edge Cases
# ============================================================================
def test_post_missing_required_field(mock_engine, sample_spec):
    """POST with missing required field must return 400."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    
    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "POST", "/users", body={"name": "Alice"}
    )
    assert status_code == 400
    assert "error" in body


def test_post_wrong_data_type_returns_400(mock_engine, sample_spec):
    """POST with wrong data type must return 400."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    
    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "POST", "/users", body={"name": "Alice", "age": "not_a_number"}
    )
    assert status_code == 400


def test_request_with_no_body_when_body_required_returns_400(mock_engine, sample_spec):
    """POST without body when body is required must return 400."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    
    status_code, body = mock_engine.handle_request(
        PROJECT_ID, "POST", "/users", body=None
    )
    assert status_code == 400


def test_empty_spec_dict(mock_engine):
    """Engine should handle empty spec gracefully."""
    empty_spec = {"paths": {}}
    mock_engine.register_spec(PROJECT_ID, empty_spec)
    
    status_code, _ = mock_engine.handle_request(PROJECT_ID, "GET", "/any-path")
    assert status_code == 404


def test_path_with_special_characters(mock_engine):
    """Engine must handle paths with special characters."""
    spec = {
        "paths": {
            "/api/v1/users-list": {
                "get": {
                    "responses": {"200": {"content": {"application/json": {"example": []}}}}
                }
            }
        }
    }
    mock_engine.register_spec(PROJECT_ID, spec)
    
    status_code, body = mock_engine.handle_request(PROJECT_ID, "GET", "/api/v1/users-list")
    assert status_code == 200


# ============================================================================
# Multiple Spec Registration Tests
# ============================================================================
def test_re_registering_project_overwrites_previous_spec(mock_engine, sample_spec):
    """Re-registering a project should replace its previous spec."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    
    new_spec = {
        "paths": {
            "/new-endpoint": {
                "get": {
                    "responses": {"200": {"content": {"application/json": {"example": {"data": "new"}}}}}
                }
            }
        }
    }
    mock_engine.register_spec(PROJECT_ID, new_spec)
    
    # Old endpoint should return 404
    status_old, _ = mock_engine.handle_request(PROJECT_ID, "GET", "/users")
    assert status_old == 404
    
    # New endpoint should work
    status_new, body_new = mock_engine.handle_request(PROJECT_ID, "GET", "/new-endpoint")
    assert status_new == 200
    assert body_new == {"data": "new"}


def test_register_multiple_endpoints_in_same_spec(mock_engine):
    """Single spec can register multiple endpoints."""
    spec = {
        "paths": {
            "/endpoint-1": {
                "get": {"responses": {"200": {"content": {"application/json": {"example": {"id": 1}}}}}}
            },
            "/endpoint-2": {
                "get": {"responses": {"200": {"content": {"application/json": {"example": {"id": 2}}}}}}
            },
            "/endpoint-3": {
                "get": {"responses": {"200": {"content": {"application/json": {"example": {"id": 3}}}}}}
            }
        }
    }
    mock_engine.register_spec(PROJECT_ID, spec)
    
    for i in range(1, 4):
        status, body = mock_engine.handle_request(PROJECT_ID, "GET", f"/endpoint-{i}")
        assert status == 200
        assert body["id"] == i


def test_post_creates_multiple_entities_sequentially(mock_engine, sample_spec):
    """Multiple POSTs should create separate entities with unique IDs."""
    mock_engine.register_spec(PROJECT_ID, sample_spec)
    
    payload_1 = {"name": "Alice", "age": 25}
    status_1, data_1 = mock_engine.handle_request(PROJECT_ID, "POST", "/users", body=payload_1)
    
    payload_2 = {"name": "Bob", "age": 30}
    status_2, data_2 = mock_engine.handle_request(PROJECT_ID, "POST", "/users", body=payload_2)
    
    assert status_1 == 201
    assert status_2 == 201
    assert data_1["id"] != data_2["id"]
    assert data_1["name"] == "Alice"
    assert data_2["name"] == "Bob"