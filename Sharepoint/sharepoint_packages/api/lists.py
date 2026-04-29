from typing import Any, Dict, List
from .base_client import SharePointClient
from .models import ListPayload, FieldPayload

class ListsAPI:
    """SharePoint Lists and List Settings endpoints."""
    def __init__(self, client: SharePointClient):
        self.client = client

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all lists in the current web."""
        response = self.client.get("web/lists")
        return response.get("d", {}).get("results", [])

    def get_by_title(self, title: str) -> Dict[str, Any]:
        """Get a specific list by its title."""
        response = self.client.get(f"web/lists/GetByTitle('{title}')")
        return response.get("d", {})

    def get_by_id(self, list_id: str) -> Dict[str, Any]:
        """Get a specific list by its GUID."""
        response = self.client.get(f"web/lists(guid'{list_id}')")
        return response.get("d", {})

    def create(self, payload: ListPayload) -> Dict[str, Any]:
        """Create a new list."""
        response = self.client.post("web/lists", data=payload.to_sp_payload())
        return response.get("d", {})

    def update(self, list_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update list settings."""
        if "__metadata" not in updates:
            updates["__metadata"] = {"type": "SP.List"}
        return self.client.patch(f"web/lists(guid'{list_id}')", data=updates)

    def delete(self, list_id: str) -> None:
        """Delete a list."""
        self.client.delete(f"web/lists(guid'{list_id}')")

    def get_fields(self, list_title: str) -> List[Dict[str, Any]]:
        """Get fields (columns) for a specific list."""
        response = self.client.get(f"web/lists/GetByTitle('{list_title}')/fields")
        return response.get("d", {}).get("results", [])

    def create_field(self, list_title: str, payload: FieldPayload) -> Dict[str, Any]:
        """Create a new column (field) in a list."""
        data = payload.to_sp_payload()
        response = self.client.post(f"web/lists/GetByTitle('{list_title}')/fields", data=data)
        return response.get("d", {})
