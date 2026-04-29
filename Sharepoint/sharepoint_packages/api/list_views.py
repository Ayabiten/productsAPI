from typing import Any, Dict, List
from .base_client import SharePointClient
from .models import ViewPayload

class ListViewsAPI:
    """SharePoint List Views endpoints."""
    def __init__(self, client: SharePointClient):
        self.client = client

    def get_views(self, list_title: str) -> List[Dict[str, Any]]:
        """Get all views for a list."""
        response = self.client.get(f"web/lists/GetByTitle('{list_title}')/views")
        return response.get("d", {}).get("results", [])

    def get_view_by_title(self, list_title: str, view_title: str) -> Dict[str, Any]:
        """Get a specific view by title."""
        response = self.client.get(f"web/lists/GetByTitle('{list_title}')/views/GetByTitle('{view_title}')")
        return response.get("d", {})

    def get_view_fields(self, list_title: str, view_title: str) -> List[str]:
        """Get the fields included in a specific view."""
        response = self.client.get(f"web/lists/GetByTitle('{list_title}')/views/GetByTitle('{view_title}')/ViewFields")
        # ViewFields structure is slightly different
        items = response.get("d", {}).get("Items", {}).get("results", [])
        return items

    def create_view(self, list_title: str, payload: ViewPayload) -> Dict[str, Any]:
        """Create a new view for a list."""
        data = payload.to_sp_payload()
        response = self.client.post(f"web/lists/GetByTitle('{list_title}')/views", data=data)
        
        # If view fields are provided, we need to add them via a separate call
        if payload.view_fields:
            for field in payload.view_fields:
                self.client.post(f"web/lists/GetByTitle('{list_title}')/views/GetByTitle('{payload.title}')/ViewFields/addViewField('{field}')")
        
        return response.get("d", {})

    def update_view(self, list_title: str, view_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing view settings by view ID (guid)."""
        if "__metadata" not in updates:
            updates["__metadata"] = {"type": "SP.View"}
        return self.client.patch(f"web/lists/GetByTitle('{list_title}')/views(guid'{view_id}')", data=updates)

    def delete_view(self, list_title: str, view_id: str) -> None:
        """Delete a view by view ID (guid)."""
        self.client.delete(f"web/lists/GetByTitle('{list_title}')/views(guid'{view_id}')")
