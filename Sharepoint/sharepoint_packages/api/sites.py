from typing import Any, Dict
from .base_client import SharePointClient

class SitesAPI:
    """SharePoint Site and Web endpoints."""
    def __init__(self, client: SharePointClient):
        self.client = client

    def get_site_properties(self) -> Dict[str, Any]:
        """Get properties of the current site collection."""
        response = self.client.get("site")
        return response.get("d", {})

    def get_web_properties(self) -> Dict[str, Any]:
        """Get properties of the current web (subsite)."""
        response = self.client.get("web")
        return response.get("d", {})
