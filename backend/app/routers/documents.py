from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
import chromadb
from chromadb.config import Settings
import os
from datetime import datetime

from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.utils.security import get_current_user
from app.schemas.document import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize Chroma client
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8002"))

chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(anonymized_telemetry=False)
)

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="advision_documents",
    metadata={"description": "Marketing documents and knowledge base"}
)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for RAG pipeline"""
    
    # Validate file type
    allowed_types = ["text/plain", "application/pdf", "text/markdown"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: txt, pdf, md")
    
    # Read file content
    content = await file.read()
    text_content = content.decode("utf-8") if file.content_type == "text/plain" else str(content)
    
    # Create document in database
    document = Document(
        organization_id=current_user.organization_id,
        title=file.filename,
        content=text_content,
        document_type="knowledge_base",
        source_url=None,
        metadata_={"uploaded_by": current_user.email}
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Add to Chroma vector DB
    collection.add(
        documents=[text_content],
        metadatas=[{
            "document_id": str(document.id),
            "organization_id": str(current_user.organization_id),
            "title": file.filename,
            "uploaded_at": datetime.utcnow().isoformat()
        }],
        ids=[f"doc_{document.id}"]
    )
    
    return document


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all documents for the organization"""
    documents = db.query(Document).filter(
        Document.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return documents


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == current_user.organization_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from Chroma
    try:
        collection.delete(ids=[f"doc_{document_id}"])
    except Exception as e:
        print(f"Error deleting from Chroma: {e}")
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}


@router.post("/query")
async def query_documents(
    query: str,
    n_results: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Query documents using RAG (Retrieval-Augmented Generation)"""
    
    # Search in Chroma
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"organization_id": str(current_user.organization_id)}
    )
    
    # Format results
    documents = []
    if results["documents"] and len(results["documents"]) > 0:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 0
            
            documents.append({
                "content": doc,
                "metadata": metadata,
                "relevance_score": 1 - distance,  # Convert distance to similarity
                "document_id": metadata.get("document_id")
            })
    
    return {
        "query": query,
        "results": documents,
        "count": len(documents)
    }
