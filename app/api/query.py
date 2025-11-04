from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag import rag_service

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_expenses(
    query_data: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Query expenses using natural language.

    **Security:** Only queries expenses belonging to the authenticated user.
    The LLM will never see or access other users' expense data.

    This endpoint uses RAG (Retrieval-Augmented Generation) to answer questions
    about your expenses using natural language.

    Examples:
        - "What were my total electric bills last quarter?"
        - "How much did I spend on water in January?"
        - "What was my highest expense last month?"
        - "Show me all expenses over $100 in the past 3 months"
        - "What's my average monthly spending on utilities?"

    Args:
        query_data: Natural language question
        db: Database session
        current_user: Current authenticated user

    Returns:
        Answer to the question with metadata
    """
    # SECURITY: Pass user_id to ensure RAG service only searches user's expenses
    answer, retrieved_count = await rag_service.answer_question(
        query_data.question, db, user_id=current_user.id
    )

    return QueryResponse(
        question=query_data.question, answer=answer, retrieved_count=retrieved_count
    )
