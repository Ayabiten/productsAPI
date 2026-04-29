from typing import Any, Dict, Optional
from ..client import ServiceNowClient

class AttachmentAPI:
    """Wrapper for the ServiceNow Attachment API (api/now/attachment)
    Reference: https://developer.servicenow.com/dev.do#!/reference/api/latest/rest/c_AttachmentAPI
    """
    
    def __init__(self, client: ServiceNowClient):
        self.client = client
        self.base_path = "api/now/attachment"

    def upload_attachment(self, table_name: str, table_sys_id: str, file_name: str, file_content: bytes, content_type: str = "text/plain") -> Dict[str, Any]:
        """Upload an attachment to a specific record."""
        path = f"{self.base_path}/file"
        params = {
            "table_name": table_name,
            "table_sys_id": table_sys_id,
            "file_name": file_name
        }
        
        # We need to temporarily override the content type for this request
        headers = {
            "Content-Type": content_type,
            "Accept": "application/json"
        }
        
        url = f"{self.client.instance_url}/{path.lstrip('/')}"
        response = self.client.session.post(url, params=params, data=file_content, headers=headers)
        response.raise_for_status()
        return response.json().get("result", {})

    def get_attachment_metadata(self, attachment_sys_id: str) -> Dict[str, Any]:
        """Get the metadata of an attachment."""
        path = f"{self.base_path}/{attachment_sys_id}"
        res = self.client.request("GET", path)
        return res.get("result", {})

    def download_attachment(self, attachment_sys_id: str) -> bytes:
        """Download the raw file content of an attachment."""
        path = f"{self.base_path}/{attachment_sys_id}/file"
        url = f"{self.client.instance_url}/{path.lstrip('/')}"
        response = self.client.session.get(url)
        response.raise_for_status()
        return response.content

    def delete_attachment(self, attachment_sys_id: str) -> bool:
        """Delete an attachment."""
        path = f"{self.base_path}/{attachment_sys_id}"
        self.client.request("DELETE", path)
        return True
