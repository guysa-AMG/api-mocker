from src.api_mocker.interface.Imock_engine import IEphemeralMockEngine
from typing import Dict, Any, Optional,Tuple

class MockEngine(IEphemeralMockEngine):
    def __init__(self):
        super().__init__()

    def register_spec(self, project_id: str, spec_dict: Dict[str, Any]) -> None:
        
    
 
    def handle_request(
        self,
        project_id: str,
        http_method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, Dict[str, Any]]: