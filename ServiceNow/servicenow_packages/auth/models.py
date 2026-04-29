from pydantic import BaseModel, Field
from typing import Optional, Literal

class AuthBase(BaseModel):
    """Base class for authentication models."""
    pass

class BasicAuthModel(AuthBase):
    """Model for ServiceNow Basic Authentication."""
    username: str
    password: str

class OAuthPasswordModel(AuthBase):
    """
    Model for ServiceNow OAuth 2.0 Resource Owner Password Credentials.
    Reference: https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/security/concept/c_OAuthResourceOwnerPasswordCredentials.html
    """
    grant_type: Literal["password"] = "password"
    client_id: str
    client_secret: str
    username: str
    password: str
    token_url: str = Field(..., description="Example: https://<instance>.service-now.com/oauth_token.do")

class OAuthClientCredentialsModel(AuthBase):
    """
    Model for ServiceNow OAuth 2.0 Client Credentials Grant.
    Reference: https://docs.servicenow.com/bundle/vancouver-platform-administration/page/administer/security/concept/c_OAuthClientCredentialsGrant.html
    """
    grant_type: Literal["client_credentials"] = "client_credentials"
    client_id: str
    client_secret: str
    token_url: str = Field(..., description="Example: https://<instance>.service-now.com/oauth_token.do")

class TokenAuthModel(AuthBase):
    """
    Model for using an existing Bearer Access Token.
    """
    access_token: str
