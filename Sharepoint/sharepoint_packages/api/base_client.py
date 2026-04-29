import requests
from requests.exceptions import RequestException
from typing import Any, Dict, Optional
from ..auth.models import SharePointToken

class SharePointAPIError(Exception):
    """Custom exception for SharePoint API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class SharePointClient:
    """Core HTTP client for SharePoint REST API."""
    def __init__(self, site_url: str, auth_token: SharePointToken):
        self.site_url = site_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose"
        })
        self.session.cookies.update(self.auth_token.get_cookies())

    def _get_headers(self) -> Dict[str, str]:
        headers = self.auth_token.get_auth_header()
        return headers

    def _handle_request_error(self, e: RequestException):
        """Helper to process request exceptions into SharePointAPIError."""
        if hasattr(e, 'response') and e.response is not None:
            raise SharePointAPIError(
                f"SharePoint API request failed: {e.response.status_code} {e.response.reason}",
                status_code=e.response.status_code,
                response_text=e.response.text
            ) from e
        raise SharePointAPIError(f"Network or connection error occurred: {str(e)}") from e

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.site_url}/_api/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            self._handle_request_error(e)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        url = f"{self.site_url}/_api/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, headers=self._get_headers(), json=data, **kwargs)
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except RequestException as e:
            self._handle_request_error(e)

    def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.site_url}/_api/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        headers["X-HTTP-Method"] = "MERGE"
        headers["If-Match"] = "*" # Or specify ETag
        try:
            response = self.session.post(url, headers=headers, json=data)
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except RequestException as e:
            self._handle_request_error(e)

    def delete(self, endpoint: str) -> None:
        url = f"{self.site_url}/_api/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        headers["X-HTTP-Method"] = "DELETE"
        headers["If-Match"] = "*"
        try:
            response = self.session.post(url, headers=headers)
            response.raise_for_status()
        except RequestException as e:
            self._handle_request_error(e)

    # Generic request for things like file uploads (binary data)
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.site_url}/_api/{endpoint.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except RequestException as e:
            self._handle_request_error(e)
