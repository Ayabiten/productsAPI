from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

# Data Payload Models for SharePoint

class ListItemPayload(BaseModel):
    """Payload model for creating or updating a List Item."""
    # The __metadata type is required for some older SP versions or specific list types
    metadata_type: Optional[str] = Field(None, alias='type')
    fields: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of field names and their values.")

    def to_sp_payload(self) -> Dict[str, Any]:
        payload = self.fields.copy()
        if self.metadata_type:
            payload['__metadata'] = {'type': self.metadata_type}
        return payload

class FileUploadMetadata(BaseModel):
    """Metadata for a file upload."""
    name: str
    content: bytes
    overwrite: bool = True

class ListPayload(BaseModel):
    """Payload model for creating a SharePoint List."""
    title: str
    description: Optional[str] = ""
    base_template: int = 100 # 100 is Custom List
    allow_content_types: bool = False

    def to_sp_payload(self) -> Dict[str, Any]:
        return {
            "__metadata": { "type": "SP.List" },
            "AllowContentTypes": self.allow_content_types,
            "BaseTemplate": self.base_template,
            "Description": self.description,
            "Title": self.title
        }

class ViewPayload(BaseModel):
    """Payload model for creating or updating a SharePoint List View."""
    title: str
    personal_view: bool = False
    view_query: Optional[str] = ""
    row_limit: int = 30
    view_fields: Optional[List[str]] = None

    def to_sp_payload(self) -> Dict[str, Any]:
        return {
            "__metadata": { "type": "SP.View" },
            "Title": self.title,
            "PersonalView": self.personal_view,
            "ViewQuery": self.view_query,
            "RowLimit": self.row_limit
        }

class FieldPayload(BaseModel):
    """Payload model for creating a SharePoint List Column (Field)."""
    title: str
    field_type_kind: int = 2 # 2 = Text, 3 = Note, 4 = DateTime, 6 = Choice, 7 = Lookup, 8 = Boolean, 9 = Number, 17 = Calculated
    required: bool = False
    read_only: bool = False
    formula: Optional[str] = None # For calculated fields (FieldTypeKind = 17)
    choices: Optional[List[str]] = None # For choice fields (FieldTypeKind = 6)
    lookup_list_id: Optional[str] = None # For lookup fields (FieldTypeKind = 7) - GUID of target list
    lookup_field_name: Optional[str] = None # For lookup fields (FieldTypeKind = 7) - Internal name of target column
    
    def to_sp_payload(self) -> Dict[str, Any]:
        # Determine the specific field type based on the kind, or default to SP.Field
        field_type_map = {
            2: "SP.FieldText",
            3: "SP.FieldMultiLineText",
            4: "SP.FieldDateTime",
            6: "SP.FieldChoice",
            7: "SP.FieldLookup",
            8: "SP.Field", # Boolean usually uses base SP.Field or SP.FieldChoice depending
            9: "SP.FieldNumber",
            17: "SP.FieldCalculated"
        }
        sp_type = field_type_map.get(self.field_type_kind, "SP.Field")
        
        payload = {
            "__metadata": { "type": sp_type },
            "Title": self.title,
            "FieldTypeKind": self.field_type_kind,
            "Required": self.required,
            "ReadOnlyField": self.read_only
        }
        
        if self.formula is not None:
            payload["Formula"] = self.formula
            
        if self.choices is not None:
            payload["Choices"] = {"results": self.choices}
            
        if self.lookup_list_id is not None:
            payload["LookupList"] = self.lookup_list_id
            
        if self.lookup_field_name is not None:
            payload["LookupField"] = self.lookup_field_name
            
        return payload
