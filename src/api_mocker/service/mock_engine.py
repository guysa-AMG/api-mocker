from typing import Any

from src.api_mocker.interface.Imock_engine import IEphemeralMockEngine


class MockEngine(IEphemeralMockEngine):

    def __init__(self):
        super().__init__()


    def register_spec(self, project_id: str, spec_dict: dict[str, Any]) -> None:
        if not self.validate_spec(spec_dict):
            return
        paths :dict= spec_dict["paths"]
        for path, value in paths.items():
            for method,value in value.items():
                route_key = f"{project_id}#{method.upper()}#{path}"
             
                self.routes[route_key]=value
                
        self._registered_specs[project_id] = spec_dict
        
    def validate_spec(self,spec_dict: dict[str, Any]) -> bool:
        # TODO Implement check logic
        return True
        
 
    def handle_request(
        self,
        project_id: str,
        http_method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        data = self._registered_specs[project_id]
        data = data["paths"]
        data = data[path]
        data = data[http_method.lower()]
        data = data["responses"]
        examples=[]
        for status,example in data.items():
            examples.append((int(status), example["content"]["application/json"]["example"]))
            
        return examples[0]
        