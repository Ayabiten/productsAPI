from typing import Any, Dict, List, Optional
from ..client import ServiceNowClient

class CSMAPI:
    """Wrapper for the ServiceNow Customer Service Management (CSM) APIs.
    References:
    - Case API: https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/c_CaseAPI
    - Account API: https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/c_AccountAPI
    """
    
    def __init__(self, client: ServiceNowClient):
        self.client = client

    # --- Case API (/api/sn_customerservice/case) ---
    def get_cases(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve a list of CSM cases."""
        path = "api/sn_customerservice/case"
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        res = self.client.request("GET", path, params=params)
        return res.get("result", [])

    def create_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new CSM case."""
        path = "api/sn_customerservice/case"
        res = self.client.request("POST", path, json=data)
        return res.get("result", {})

    def update_case(self, sys_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing CSM case."""
        path = f"api/sn_customerservice/case/{sys_id}"
        res = self.client.request("PATCH", path, json=data)
        return res.get("result", {})

    # --- Account API (/api/now/account) ---
    def get_accounts(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve a list of accounts."""
        path = "api/now/account"
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        res = self.client.request("GET", path, params=params)
        return res.get("result", [])

    def create_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new account."""
        path = "api/now/account"
        res = self.client.request("POST", path, json=data)
        return res.get("result", {})

    def get_account(self, sys_id: str) -> Dict[str, Any]:
        """Retrieve a single account by sys_id."""
        path = f"api/now/account/{sys_id}"
        res = self.client.request("GET", path)
        return res.get("result", {})
