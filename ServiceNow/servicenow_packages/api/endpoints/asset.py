from typing import Any, Dict, List, Optional
from ..client import ServiceNowClient

class AssetAPI:
    """Wrapper for ServiceNow Asset Management APIs.
    Includes Enterprise Asset Management (AI Assets) and standard Table API for alm_asset.
    Reference: https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/c_AIAssetsAPI
    """
    
    def __init__(self, client: ServiceNowClient):
        self.client = client

    # --- AI Assets API (/api/sn_ent/asset) ---
    def get_enterprise_assets(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve enterprise assets using the AI Assets API."""
        path = "api/sn_ent/asset"
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        res = self.client.request("GET", path, params=params)
        return res.get("result", [])

    # --- Standard Asset Management (via Table API) ---
    def get_assets(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve assets from the alm_asset table."""
        path = "api/now/table/alm_asset"
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        res = self.client.request("GET", path, params=params)
        return res.get("result", [])

    def create_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new asset record."""
        path = "api/now/table/alm_asset"
        res = self.client.request("POST", path, json=data)
        return res.get("result", {})
