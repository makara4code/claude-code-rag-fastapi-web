from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Schema for natural language query request."""

    question: str = Field(..., min_length=1, description="Natural language question about expenses")


class QueryResponse(BaseModel):
    """Schema for natural language query response."""

    question: str
    answer: str
    retrieved_count: int = Field(..., description="Number of expense records retrieved")
