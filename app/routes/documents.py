from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse
from typing import List

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new HR policy document
    
    - **name**: Document name (required)
    - **description**: Document description (optional)
    - **link**: SharePoint link to the document (required)
    """
    db_document = Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/", response_model=DocumentListResponse)
def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    location: str = Query(None, description="Filter documents by location"),
    db: Session = Depends(get_db)
):
    """
    Get all HR policy documents with pagination and optional location filter
    
    - **skip**: Number of documents to skip (default: 0)
    - **limit**: Maximum number of documents to return (default: 100, max: 1000)
    - **location**: Location to filter documents by (e.g., "India", "USA")
    """
    query = db.query(Document)
    if location:
        query = query.filter(Document.location.ilike(f"%{location}%"))
    
    total = query.count()
    documents = query.offset(skip).limit(limit).all()

    # Convert ORM objects to Pydantic models to satisfy response_model validation
    from app.schemas.document import DocumentListResponse, DocumentResponse

    docs_out = [DocumentResponse.from_orm(d) for d in documents]
    return DocumentListResponse(total=total, documents=docs_out)

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific HR policy document by ID
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )
    return db_document

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an HR policy document
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )
    
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an HR policy document
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )
    
    db.delete(db_document)
    db.commit()
    return None

@router.get("/{document_id}/link")
def get_document_link(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the SharePoint link for a document (for viewing)
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found"
        )
    
    return {"link": db_document.link}
