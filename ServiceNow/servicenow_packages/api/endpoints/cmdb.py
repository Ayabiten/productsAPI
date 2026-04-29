from typing import Any, Dict, List, Optional
from ..client import ServiceNowClient

class CMDBAPI:
    """Wrapper for the ServiceNow CMDB Instance API.
    Reference: https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/c_CMDBInstanceAPI
    """
    
    def __init__(self, client: ServiceNowClient):
        self.client = client
        self.base_path = "api/now/cmdb/instance"

    def get_ci_instances(self, class_name: str, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve instances of a specific CI class."""
        path = f"{self.base_path}/{class_name}"
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        res = self.client.request("GET", path, params=params)
        return res.get("result", [])

    def create_ci_instance(self, class_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new CI instance."""
        path = f"{self.base_path}/{class_name}"
        res = self.client.request("POST", path, json=data)
        return res.get("result", {})

    def update_ci_instance(self, class_name: str, sys_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing CI instance."""
        path = f"{self.base_path}/{class_name}/{sys_id}"
        res = self.client.request("PATCH", path, json=data)
        return res.get("result", {})

    def delete_ci_instance(self, class_name: str, sys_id: str) -> bool:
        """Delete a CI instance."""
        path = f"{self.base_path}/{class_name}/{sys_id}"
        self.client.request("DELETE", path)
        return True
