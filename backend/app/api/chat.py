"""
Chat & Evidence-First RAG API Router for DocuPilot.
Coordinates semantic retrieval, anti-hallucination gates, Groq LLM generation, and verified source attribution.
"""

from fastapi import APIRouter, HTTPException, status
from app.core.logging import logger
from app.models.schemas import ChatRequest, ChatResponse, ChatStatus, ConfidenceLevel
from app.services.llm import llm_service
from app.services.retriever import retriever_service
from app.services.vector_store import vector_store_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query_knowledge_base(request: ChatRequest):
    """
    Executes Evidence-First RAG QA:
    1. Validates question length and input
    2. Checks if any documents are indexed
    3. Retrieves top-K semantically similar chunks with relevance threshold filtering
    4. Anti-Hallucination Gate: If no evidence passes threshold, returns deterministic NOT_FOUND immediately
    5. Calls LLM with only the 2-4 verified context chunks
    6. Maps returned source citations back to verified source metadata
    7. Returns structured JSON answer with Evidence Trail
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Check if there are any documents in the knowledge base
    registered_docs = vector_store_service.get_all_documents()
    if not registered_docs:
        return ChatResponse(
            status=ChatStatus.NOT_FOUND,
            answer=(
                "Your knowledge workspace is empty. Please upload one or more business documents "
                "(PDF or TXT) to ask questions."
            ),
            confidence=ConfidenceLevel.LOW,
            sources=[],
            suggested_followups=[]
        )

    logger.info(f"Received query: '{question}' (Active documents: {len(registered_docs)})")

    # 1. Retrieve relevant evidence chunks
    try:
        retrieved_sources = retriever_service.retrieve(
            query=question,
            document_id_filter=request.document_id
        )
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve evidence from vector store.")

    # 2. Anti-Hallucination gate: If no chunks pass similarity threshold, do not invoke LLM
    if not retrieved_sources:
        logger.info(f"Query '{question}' produced no high-relevance evidence. Returning NOT_FOUND.")
        return ChatResponse(
            status=ChatStatus.NOT_FOUND,
            answer=(
                "I couldn't find supporting information for this question in the uploaded documents.\n\n"
                "No evidence met the required relevance threshold. Please try asking about topics "
                "covered in your uploaded documents."
            ),
            confidence=ConfidenceLevel.LOW,
            sources=[],
            suggested_followups=[
                "What policies are detailed in the uploaded documents?",
                "What are the main employee benefits?",
                "What is the company leave entitlement?"
            ]
        )

    # 3. Generate grounded answer via LLM Provider
    try:
        response = llm_service.generate_answer(
            question=question,
            sources=retrieved_sources,
            conversation_history=request.conversation_history,
            document_scope=request.document_id
        )
        return response
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        raise HTTPException(status_code=500, detail=f"Answer generation error: {str(e)}")
