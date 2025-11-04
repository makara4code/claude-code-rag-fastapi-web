from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag import rag_service

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_expenses(query_data: QueryRequest, db: Session = Depends(get_db)):
    """
    Query expenses using natural language.

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

    Returns:
        Answer to the question with metadata
    """
    answer, retrieved_count = await rag_service.answer_question(query_data.question, db)

    return QueryResponse(
        question=query_data.question, answer=answer, retrieved_count=retrieved_count
    )
