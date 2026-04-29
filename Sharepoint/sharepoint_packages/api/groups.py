from typing import Any, Dict, List
from .base_client import SharePointClient

class GroupsAPI:
    """SharePoint Access Groups and Users endpoints."""
    def __init__(self, client: SharePointClient):
        self.client = client

    def get_site_groups(self) -> List[Dict[str, Any]]:
        """Get all groups for the site collection."""
        response = self.client.get("web/sitegroups")
        return response.get("d", {}).get("results", [])

    def get_group_by_name(self, name: str) -> Dict[str, Any]:
        """Get a specific group by name."""
        response = self.client.get(f"web/sitegroups/getbyname('{name}')")
        return response.get("d", {})

    def get_users_in_group(self, group_name: str) -> List[Dict[str, Any]]:
        """Get users within a specific group."""
        response = self.client.get(f"web/sitegroups/getbyname('{group_name}')/users")
        return response.get("d", {}).get("results", [])

    def get_current_user(self) -> Dict[str, Any]:
        """Get the current authenticated user."""
        response = self.client.get("web/currentuser")
        return response.get("d", {})

    def create_group(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new SharePoint group."""
        payload = {
            "__metadata": {"type": "SP.Group"},
            "Title": name,
            "Description": description
        }
        response = self.client.post("web/sitegroups", data=payload)
        return response.get("d", {})
