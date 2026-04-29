from typing import Any, Dict, List
from .base_client import SharePointClient

class RolesAPI:
    """SharePoint Roles and Role Assignments endpoints."""
    def __init__(self, client: SharePointClient):
        self.client = client

    def get_role_definitions(self) -> List[Dict[str, Any]]:
        """Get all role definitions (Permission Levels) for the site."""
        response = self.client.get("web/roledefinitions")
        return response.get("d", {}).get("results", [])

    def get_role_definition_by_name(self, name: str) -> Dict[str, Any]:
        """Get a specific role definition by name."""
        response = self.client.get(f"web/roledefinitions/getbyname('{name}')")
        return response.get("d", {})

    def add_role_assignment(self, principal_id: int, role_def_id: int, target: str = "web") -> None:
        """
        Assign a role to a principal (user/group).
        :param target: Can be 'web' or 'lists/getbytitle("Title")'
        """
        endpoint = f"web/{target}/roleassignments/addroleassignment(principalid={principal_id},roledefid={role_def_id})"
        self.client.post(endpoint)

    def remove_role_assignment(self, principal_id: int, role_def_id: int, target: str = "web") -> None:
        """
        Remove a role assignment.
        """
        endpoint = f"web/{target}/roleassignments/removeroleassignment(principalid={principal_id},roledefid={role_def_id})"
        self.client.post(endpoint)
        
    def break_role_inheritance(self, list_title: str, copy_role_assignments: bool = True, clear_subscopes: bool = True) -> None:
        """Break inheritance for a specific list."""
        endpoint = f"web/lists/GetByTitle('{list_title}')/breakroleinheritance(copyRoleAssignments={str(copy_role_assignments).lower()}, clearSubscopes={str(clear_subscopes).lower()})"
        self.client.post(endpoint)
