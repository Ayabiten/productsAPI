from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class ServiceNowResponse(BaseModel):
    """Model for a generic ServiceNow API response."""
    result: Any

class ServiceNowErrorDetail(BaseModel):
    """Model for detailed error information."""
    message: str
    detail: Optional[str] = None

class ServiceNowError(BaseModel):
    """Model for a ServiceNow API error response."""
    error: ServiceNowErrorDetail
    status: str

class RecordQueryModel(BaseModel):
    """Model for querying records."""
    table_name: str
    sysparm_query: Optional[str] = None
    sysparm_limit: int = 100
    sysparm_offset: int = 0
    sysparm_fields: Optional[List[str]] = None

class RecordCreateModel(BaseModel):
    """Model for creating a record."""
    table_name: str
    data: Dict[str, Any]

class RecordUpdateModel(BaseModel):
    """Model for updating a record."""
    table_name: str
    sys_id: str
    data: Dict[str, Any]
