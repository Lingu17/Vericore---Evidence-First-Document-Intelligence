"""
Document Management API Router for DocuPilot.
Handles document uploads, SHA-256 deduplication, parsing, chunking, embedding, indexing, and suggestions.
"""

import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.core.logging import logger
from app.models.schemas import (
    DocumentDetail,
    DocumentListResponse,
    DocumentUploadResponse,
    SuggestedQuestionsResponse,
)
from app.services.chunker import DocumentChunker
from app.services.document_parser import DocumentParser, DocumentParserError
from app.services.embeddings import embedding_service
from app.services.suggestions import generate_suggested_questions
from app.services.vector_store import vector_store_service
from app.utils.hashing import calculate_sha256

router = APIRouter(prefix="/api/documents", tags=["Documents"])
chunker = DocumentChunker()


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """Returns list of all indexed documents in the workspace."""
    docs = vector_store_service.get_all_documents()
    items = [
        DocumentDetail(
            document_id=d.document_id,
            filename=d.filename,
            file_type=d.file_type,
            pages=d.page_count,
            chunks=d.chunk_count,
            status=d.status.value,
            created_at=d.created_at,
            suggested_questions=d.suggested_questions
        )
        for d in docs
    ]
    return DocumentListResponse(total=len(items), documents=items)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a business document (PDF/TXT):
    1. Validates file format and length
    2. Calculates SHA-256 file hash for deduplication
    3. If hash exists, returns existing document immediately (no wasted compute)
    4. Parses document into pages and structured headings
    5. Chunks text with page and section metadata
    6. Generates vector embeddings locally (all-MiniLM-L6-v2)
    7. Indexes into ChromaDB
    8. Generates 3-5 smart suggested questions
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing in upload.")

    filename = file.filename
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read upload stream: {e}")
        raise HTTPException(status_code=400, detail="Could not read uploaded file content.")

    # 1. SHA-256 Deduplication check
    file_hash = calculate_sha256(content)
    existing_doc = vector_store_service.document_exists_by_hash(file_hash)
    if existing_doc:
        logger.info(f"Duplicate upload detected for '{filename}' (Doc ID: {existing_doc.document_id}).")
        return DocumentUploadResponse(
            document_id=existing_doc.document_id,
            filename=existing_doc.filename,
            pages=existing_doc.page_count,
            chunks=existing_doc.chunk_count,
            status="already_exists",
            message="This document is already indexed.",
            suggested_questions=existing_doc.suggested_questions
        )

    # 2. Parse document
    try:
        parsed_doc = DocumentParser.parse(filename, content)
    except DocumentParserError as e:
        logger.warning(f"Validation/Parsing error for '{filename}': {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected parsing failure for '{filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

    # 3. Generate unique document ID
    doc_id = f"doc_{uuid.uuid4().hex[:10]}"

    # 4. Chunk document
    chunks = chunker.chunk_document(doc_id, parsed_doc)
    if not chunks:
        raise HTTPException(status_code=400, detail="Document contained no extractable textual chunks.")

    # 5. Generate local embeddings
    chunk_texts = [c.text for c in chunks]
    try:
        embeddings = embedding_service.embed_batch(chunk_texts)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate local embeddings for document.")

    # 6. Generate suggested questions
    suggested_questions = generate_suggested_questions(
        filename=filename,
        headings=parsed_doc.headings,
        full_text=parsed_doc.full_text
    )

    # 7. Index into ChromaDB & persist metadata
    try:
        doc_meta = vector_store_service.add_document_chunks(
            document_id=doc_id,
            filename=filename,
            file_type=parsed_doc.file_type,
            file_hash=file_hash,
            page_count=parsed_doc.total_pages,
            chunks=chunks,
            embeddings=embeddings,
            suggested_questions=suggested_questions
        )
    except Exception as e:
        logger.error(f"ChromaDB indexing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store vectors in database: {str(e)}")

    logger.info(f"Document upload & indexing pipeline complete: '{filename}' ({doc_meta.chunk_count} chunks).")
    return DocumentUploadResponse(
        document_id=doc_meta.document_id,
        filename=doc_meta.filename,
        pages=doc_meta.page_count,
        chunks=doc_meta.chunk_count,
        status="indexed",
        message="Document successfully processed and indexed.",
        suggested_questions=doc_meta.suggested_questions
    )


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(document_id: str):
    """Fetches details for a specific document."""
    doc = vector_store_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return DocumentDetail(
        document_id=doc.document_id,
        filename=doc.filename,
        file_type=doc.file_type,
        pages=doc.page_count,
        chunks=doc.chunk_count,
        status=doc.status.value,
        created_at=doc.created_at,
        suggested_questions=doc.suggested_questions
    )


@router.get("/{document_id}/suggestions", response_model=SuggestedQuestionsResponse)
async def get_document_suggestions(document_id: str):
    """Retrieves suggested questions for a specific indexed document."""
    doc = vector_store_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return SuggestedQuestionsResponse(
        document_id=doc.document_id,
        filename=doc.filename,
        questions=doc.suggested_questions
    )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: str):
    """Deletes a document and purges its vector embeddings from ChromaDB."""
    deleted = vector_store_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")

    return {"status": "success", "message": f"Document {document_id} and its vector chunks deleted."}


@router.delete("", status_code=status.HTTP_200_OK)
async def clear_all_documents():
    """Clears all indexed documents from the workspace."""
    vector_store_service.delete_all()
    return {"status": "success", "message": "All documents cleared from knowledge base."}
