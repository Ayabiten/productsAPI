from typing import Any, Dict, Optional
from ..client import ServiceNowClient

class AggregateAPI:
    """Wrapper for the ServiceNow Aggregate API (api/now/stats)
    Reference: https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/c_AggregateAPI
    """
    
    def __init__(self, client: ServiceNowClient):
        self.client = client
        self.base_path = "api/now/stats"

    def get_stats(self, table_name: str, query: Optional[str] = None, count: bool = True, sum_field: Optional[str] = None, avg_field: Optional[str] = None, group_by: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve aggregate statistics (count, sum, avg) for a table."""
        path = f"{self.base_path}/{table_name}"
        params = {}
        
        if query:
            params["sysparm_query"] = query
        if count:
            params["sysparm_count"] = "true"
        if sum_field:
            params["sysparm_sum_fields"] = sum_field
        if avg_field:
            params["sysparm_avg_fields"] = avg_field
        if group_by:
            params["sysparm_group_by"] = group_by
            
        res = self.client.request("GET", path, params=params)
        return res.get("result", {})
