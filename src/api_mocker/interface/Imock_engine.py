from abc import ABC, abstractmethod
from typing import Any


class IEphemeralMockEngine(ABC):
    """In-memory mock engine for parsing OpenAPI specifications and

    simulating API behavior, state persistence, schema validation,
    and artificial latency.
    """

    def __init__(self) -> None:
        """Initialize in-memory storage for registered routes and state."""
        self.routes: dict[str, Any] = {}
        self._registered_specs: dict[str, Any] = {}
        self.state_store: dict[str, Any] = {}

    @abstractmethod
    def register_spec(self, project_id: str, spec_dict: dict[str, Any]) -> None:
        """Parse an OpenAPI specification dictionary and store route configurations.

        :param project_id: Unique identifier for the project scope.
        :param spec_dict: Raw OpenAPI spec loaded as a Python dictionary.
        """
        ...

    @abstractmethod
    def handle_request(
        self,
        project_id: str,
        http_method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        """Process an incoming HTTP request, validate schema, handle state,

        simulate latency, and return a status code and response payload.

        :param project_id: Unique identifier for the project scope.
        :param http_method: HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        :param path: The requested URL path (e.g., '/users' or '/users/123').
        :param body: Optional JSON payload dictionary for POST/PUT requests.
        :return: A tuple of (HTTP status code, response body dictionary).
        """
        ...