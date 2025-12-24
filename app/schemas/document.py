from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Document name")
    description: Optional[str] = Field(None, description="Document description")
    link: str = Field(..., min_length=1, max_length=500, description="SharePoint link to the document")
    location: str = Field("India", min_length=1, max_length=100, description="Location of the policy document")

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    link: Optional[str] = Field(None, min_length=1, max_length=500)
    location: Optional[str] = Field(None, min_length=1, max_length=100)

class DocumentResponse(DocumentBase):
    id: int
    last_updated: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DocumentListResponse(BaseModel):
    total: int
    documents: list[DocumentResponse]
