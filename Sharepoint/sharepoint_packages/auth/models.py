from typing import Optional
from datetime import datetime

class SharePointToken:
    """Base class for SharePoint Authentication Tokens."""
    def __init__(self, access_token: str, expires_on: Optional[datetime] = None, token_type: str = "Bearer"):
        self.access_token = access_token
        self.expires_on = expires_on
        self.token_type = token_type

    def get_auth_header(self) -> dict:
        return {"Authorization": f"{self.token_type} {self.access_token}"}

    def get_cookies(self) -> dict:
        return {}

    def is_expired(self) -> bool:
        if self.expires_on:
            return datetime.utcnow() >= self.expires_on
        return False

class ClientCredentialsToken(SharePointToken):
    """Token generated using Azure AD Client ID and Client Secret (App-Only)."""
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, scope: str = "https://graph.microsoft.com/.default"):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        
        token, expires = self._fetch_token()
        super().__init__(access_token=token, expires_on=expires, token_type="Bearer")

    def _fetch_token(self):
        import requests
        from datetime import timedelta
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        resp_data = response.json()
        expires_on = datetime.utcnow() + timedelta(seconds=resp_data.get("expires_in", 3599))
        return resp_data["access_token"], expires_on

class UserCredentialsToken(SharePointToken):
    """Token generated using Username and Password (ROPC Flow)."""
    def __init__(self, tenant_id: str, client_id: str, username: str, password: str, scope: str = "https://graph.microsoft.com/.default"):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.username = username
        self.password = password
        self.scope = scope
        
        token, expires = self._fetch_token()
        super().__init__(access_token=token, expires_on=expires, token_type="Bearer")

    def _fetch_token(self):
        import requests
        from datetime import timedelta
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
            "scope": self.scope
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        resp_data = response.json()
        expires_on = datetime.utcnow() + timedelta(seconds=resp_data.get("expires_in", 3599))
        return resp_data["access_token"], expires_on

class CookieAuthToken(SharePointToken):
    """Token using FedAuth and rtFa cookies from a browser session."""
    def __init__(self, fed_auth: str, rt_fa: str):
        super().__init__(access_token="")
        self.fed_auth = fed_auth
        self.rt_fa = rt_fa

    def get_auth_header(self) -> dict:
        return {} # No Authorization header needed if using cookies

    def get_cookies(self) -> dict:
        return {
            "FedAuth": self.fed_auth,
            "rtFa": self.rt_fa
        }

class LocalBrowserAuthToken(SharePointToken):
    """
    Automatically extracts FedAuth and rtFa cookies from the local Windows Chrome/Edge database.
    Requires: pip install pywin32 cryptography
    """
    def __init__(self, domain: str, browser: str = "chrome"):
        super().__init__(access_token="")
        self.fed_auth, self.rt_fa = self._extract_cookies_from_db(domain, browser)

    def get_auth_header(self) -> dict:
        return {} 

    def get_cookies(self) -> dict:
        return {
            "FedAuth": self.fed_auth,
            "rtFa": self.rt_fa
        }

    def _extract_cookies_from_db(self, domain: str, browser: str):
        import os
        import json
        import base64
        import sqlite3
        import shutil
        import tempfile
        try:
            import win32crypt
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            raise ImportError("Please install required packages: pip install pywin32 cryptography")

        local_app_data = os.environ.get('LOCALAPPDATA')
        if not local_app_data:
            raise EnvironmentError("LOCALAPPDATA environment variable not found. Are you on Windows?")

        # 1. Get the encrypted key
        if browser.lower() == "chrome":
            local_state_path = os.path.join(local_app_data, r"Google\Chrome\User Data\Local State")
            cookie_db_path = os.path.join(local_app_data, r"Google\Chrome\User Data\Default\Network\Cookies")
        elif browser.lower() == "edge":
            local_state_path = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Local State")
            cookie_db_path = os.path.join(local_app_data, r"Microsoft\Edge\User Data\Default\Network\Cookies")
        else:
            raise ValueError("Unsupported browser. Use 'chrome' or 'edge'.")

        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())

        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        # 2. Query the SQLite DB
        if not os.path.exists(cookie_db_path):
            raise FileNotFoundError(f"Cookie database not found at {cookie_db_path}")

        # Copy to temp file to avoid 'database is locked' errors
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, "temp_browser_cookies.sqlite")
        shutil.copy2(cookie_db_path, temp_db_path)

        fed_auth = None
        rt_fa = None

        try:
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name, encrypted_value FROM cookies WHERE host_key LIKE ?", (f"%{domain}%",))
            
            for name, encrypted_value in cursor.fetchall():
                if name in ["FedAuth", "rtFa"]:
                    # Decrypt AES-GCM
                    nonce = encrypted_value[3:15]
                    ciphertext = encrypted_value[15:]
                    aesgcm = AESGCM(decrypted_key)
                    decrypted_val = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
                    
                    if name == "FedAuth":
                        fed_auth = decrypted_val
                    elif name == "rtFa":
                        rt_fa = decrypted_val
        finally:
            conn.close()
            try:
                os.remove(temp_db_path)
            except Exception:
                pass

        if not fed_auth or not rt_fa:
            raise ValueError(f"Could not find FedAuth or rtFa cookies for {domain} in {browser}.")

        return fed_auth, rt_fa

