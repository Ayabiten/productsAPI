from typing import Any, Dict, List, Optional
from ..client import ServiceNowClient

class AgentAPI:
    """Wrapper for the ServiceNow Agent Client Collector API.
    Reference: https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/c_AgentClientCollectorAPI
    """
    
    def __init__(self, client: ServiceNowClient):
        self.client = client
        self.base_path = "api/sn_agent"

    def get_agents(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve a list of agents."""
        path = f"{self.base_path}/agents"
        params = {"sysparm_limit": limit}
        if query:
            params["sysparm_query"] = query
        res = self.client.request("GET", path, params=params)
        return res.get("result", [])

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve the status of a specific agent."""
        path = f"{self.base_path}/agents/{agent_id}/status"
        res = self.client.request("GET", path)
        return res.get("result", {})

    def run_check(self, agent_id: str, check_id: str) -> Dict[str, Any]:
        """Run a specific check on an agent."""
        path = f"{self.base_path}/agents/{agent_id}/checks/{check_id}/run"
        res = self.client.request("POST", path)
        return res.get("result", {})
