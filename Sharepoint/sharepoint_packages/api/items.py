from typing import Any, Dict, List
from .base_client import SharePointClient
from .models import ListItemPayload

class ItemsAPI:
    """SharePoint List Items (CRUD) and Data Upload endpoints."""
    def __init__(self, client: SharePointClient):
        self.client = client

    def get_items(self, list_title: str, select: str = "", filter_query: str = "") -> List[Dict[str, Any]]:
        """Get items from a list with optional OData filters."""
        params = {}
        if select:
            params["$select"] = select
        if filter_query:
            params["$filter"] = filter_query
        
        response = self.client.get(f"web/lists/GetByTitle('{list_title}')/items", params=params)
        return response.get("d", {}).get("results", [])

    def get_item_by_id(self, list_title: str, item_id: int) -> Dict[str, Any]:
        """Get a single item by its ID."""
        response = self.client.get(f"web/lists/GetByTitle('{list_title}')/items({item_id})")
        return response.get("d", {})

    def create_item(self, list_title: str, payload: ListItemPayload) -> Dict[str, Any]:
        """Create/Upload a new item to a list."""
        data = payload.to_sp_payload()
        response = self.client.post(f"web/lists/GetByTitle('{list_title}')/items", data=data)
        return response.get("d", {})

    def update_item(self, list_title: str, item_id: int, payload: ListItemPayload) -> Dict[str, Any]:
        """Update an existing item."""
        data = payload.to_sp_payload()
        return self.client.patch(f"web/lists/GetByTitle('{list_title}')/items({item_id})", data=data)

    def delete_item(self, list_title: str, item_id: int) -> None:
        """Delete an item from a list."""
        self.client.delete(f"web/lists/GetByTitle('{list_title}')/items({item_id})")
