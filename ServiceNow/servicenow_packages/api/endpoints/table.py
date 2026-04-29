from typing import Any, Dict, List, Optional
from ..client import ServiceNowClient

class TableAPI:
    """Wrapper for the ServiceNow Table API (api/now/table)"""
    
    def __init__(self, client: ServiceNowClient):
        self.client = client
        self.base_path = "api/now/table"

    def get_records(self, table_name: str, query: Optional[str] = None, limit: int = 100, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Retrieve multiple records from a table."""
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        if fields:
            params["sysparm_fields"] = ",".join(fields)
            
        path = f"{self.base_path}/{table_name}"
        res = self.client.request("GET", path, params=params)
        return res.get("result", [])

    def get_record(self, table_name: str, sys_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Retrieve a single record by its sys_id."""
        params = {}
        if fields:
            params["sysparm_fields"] = ",".join(fields)
            
        path = f"{self.base_path}/{table_name}/{sys_id}"
        res = self.client.request("GET", path, params=params)
        return res.get("result", {})

    def create_record(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in a table."""
        path = f"{self.base_path}/{table_name}"
        res = self.client.request("POST", path, json=data)
        return res.get("result", {})

    def update_record(self, table_name: str, sys_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record."""
        path = f"{self.base_path}/{table_name}/{sys_id}"
        res = self.client.request("PATCH", path, json=data)
        return res.get("result", {})
        
    def replace_record(self, table_name: str, sys_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace an existing record."""
        path = f"{self.base_path}/{table_name}/{sys_id}"
        res = self.client.request("PUT", path, json=data)
        return res.get("result", {})

    def delete_record(self, table_name: str, sys_id: str) -> bool:
        """Delete a record."""
        path = f"{self.base_path}/{table_name}/{sys_id}"
        self.client.request("DELETE", path)
        return True
