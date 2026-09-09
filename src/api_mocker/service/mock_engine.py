from src.api_mocker.interface.Imock_engine import IEphemeralMockEngine
from typing import Dict, Any, Optional,Tuple

class MockEngine(IEphemeralMockEngine):
    _registered_specs: Dict
    routes: Dict
    def __init__(self):
        super().__init__()
        self._registered_specs = dict();
        self.routes = dict()

    def register_spec(self, project_id: str, spec_dict: Dict[str, Any]) -> None:
        if not self.validate_spec(spec_dict):
            return
        paths :dict= spec_dict["paths"]
        for path in paths.keys():
            for method in paths[path].keys():
                route_key = f"{project_id}#{method.upper()}#{path}"
                route_value = paths[path][method]
                self.routes[route_key]=route_value
                
        self._registered_specs[project_id] = spec_dict
        
    def validate_spec(self,spec_dict: Dict[str, Any]) -> bool:
        # TODO Implement check logic
        return True
        
 
    def handle_request(
        self,
        project_id: str,
        http_method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        pass