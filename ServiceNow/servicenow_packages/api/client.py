import requests
from typing import Any, Dict, Optional, Union
from ..auth.models import (
    BasicAuthModel, 
    OAuthPasswordModel, 
    OAuthClientCredentialsModel, 
    TokenAuthModel
)

class ServiceNowClient:
    """Client for interacting with the ServiceNow REST API."""
    
    def __init__(self, instance_url: str, auth: Union[BasicAuthModel, OAuthPasswordModel, OAuthClientCredentialsModel, TokenAuthModel]):
        self.instance_url = instance_url.rstrip("/")
        self.auth = auth
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self._setup_auth()

    def _setup_auth(self):
        """Configure the session authentication based on the provided auth model."""
        if isinstance(self.auth, BasicAuthModel):
            self.session.auth = (self.auth.username, self.auth.password)
        elif isinstance(self.auth, TokenAuthModel):
            self.session.headers.update({"Authorization": f"Bearer {self.auth.access_token}"})
        elif isinstance(self.auth, (OAuthPasswordModel, OAuthClientCredentialsModel)):
            token = self._get_oauth_token()
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _get_oauth_token(self) -> str:
        """Fetch an OAuth 2.0 access token from ServiceNow."""
        if not isinstance(self.auth, (OAuthPasswordModel, OAuthClientCredentialsModel)):
            raise ValueError("Auth model must be an OAuth model to fetch a token.")

        payload = {
            "grant_type": self.auth.grant_type,
            "client_id": self.auth.client_id,
            "client_secret": self.auth.client_secret
        }

        if isinstance(self.auth, OAuthPasswordModel):
            payload["username"] = self.auth.username
            payload["password"] = self.auth.password

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(self.auth.token_url, data=payload, headers=headers)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data.get("access_token")

    def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the ServiceNow API."""
        url = f"{self.instance_url}/{path.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        
        # Handle empty responses (like 204 No Content for DELETE)
        if response.status_code == 204:
            return {}
            
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                raise Exception(f"ServiceNow API Error: {error_data}") from e
            except ValueError:
                raise e
