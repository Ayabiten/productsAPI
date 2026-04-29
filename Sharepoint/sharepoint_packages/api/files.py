from typing import Any, Dict, List
from .base_client import SharePointClient
from .models import FileUploadMetadata

class FilesAPI:
    """SharePoint Files and Folders endpoints."""
    def __init__(self, client: SharePointClient):
        self.client = client

    def get_folder_by_server_relative_url(self, url: str) -> Dict[str, Any]:
        """Get folder properties."""
        response = self.client.get(f"web/GetFolderByServerRelativeUrl('{url}')")
        return response.get("d", {})

    def get_files_in_folder(self, folder_url: str) -> List[Dict[str, Any]]:
        """Get all files within a specific folder."""
        response = self.client.get(f"web/GetFolderByServerRelativeUrl('{folder_url}')/files")
        return response.get("d", {}).get("results", [])

    def upload_file(self, folder_url: str, file_meta: FileUploadMetadata) -> Dict[str, Any]:
        """Upload a file to a folder."""
        endpoint = f"web/GetFolderByServerRelativeUrl('{folder_url}')/files/add(url='{file_meta.name}',overwrite={str(file_meta.overwrite).lower()})"
        headers = {
            "Accept": "application/json;odata=verbose",
        }
        # For binary upload, we don't send json=data, we send data=bytes
        response = self.client.request("POST", endpoint, headers=headers, data=file_meta.content)
        return response.json().get("d", {})

    def download_file(self, file_url: str) -> bytes:
        """Download file content."""
        endpoint = f"web/GetFileByServerRelativeUrl('{file_url}')/$value"
        # Standard Accept header might fail for raw binary in some versions, but base client handles generic requests
        response = self.client.request("GET", endpoint)
        return response.content

    def delete_file(self, file_url: str) -> None:
        """Delete a file."""
        self.client.delete(f"web/GetFileByServerRelativeUrl('{file_url}')")
