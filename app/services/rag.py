from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.expense import Expense
from app.services.embedding import embedding_service
from app.services.ollama import ollama_service


class RAGService:
    """Service for RAG-based query answering."""

    def __init__(self):
        """Initialize RAG service."""
        self.embedding_service = embedding_service
        self.ollama_service = ollama_service

    async def search_similar_expenses(
        self, query: str, db: Session, top_k: int = 10
    ) -> List[Expense]:
        """
        Search for expenses similar to the query using vector similarity.

        Args:
            query: Search query
            db: Database session
            top_k: Number of results to return

        Returns:
            List of similar expense records
        """
        # Generate embedding for the query
        query_embedding = self.embedding_service.generate_query_embedding(query)

        # Convert numpy array to list for PostgreSQL
        embedding_list = query_embedding.tolist()

        # Perform vector similarity search using pgvector
        # Using cosine distance (1 - cosine_similarity)
        sql = text(
            """
            SELECT * FROM expenses
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """
        )

        result = db.execute(sql, {"embedding": str(embedding_list), "limit": top_k})
        expenses = []

        for row in result:
            expense = Expense(
                id=row.id,
                category=row.category,
                amount=row.amount,
                date=row.date,
                description=row.description,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            expenses.append(expense)

        return expenses

    def format_expenses_as_context(self, expenses: List[Expense]) -> str:
        """
        Format expense records as context for LLM.

        Args:
            expenses: List of expense records

        Returns:
            Formatted context string
        """
        if not expenses:
            return "No relevant expense records found."

        context_parts = []
        for i, expense in enumerate(expenses, 1):
            expense_text = (
                f"{i}. Category: {expense.category}, "
                f"Amount: ${expense.amount}, "
                f"Date: {expense.date.strftime('%Y-%m-%d')}"
            )
            if expense.description:
                expense_text += f", Description: {expense.description}"

            context_parts.append(expense_text)

        return "\n".join(context_parts)

    async def answer_question(self, question: str, db: Session) -> tuple[str, int]:
        """
        Answer a natural language question about expenses using RAG.

        Args:
            question: User's question
            db: Database session

        Returns:
            Tuple of (answer, number of records retrieved)
        """
        # Step 1: Retrieve relevant expenses
        relevant_expenses = await self.search_similar_expenses(question, db, top_k=10)

        # Step 2: Format expenses as context
        context = self.format_expenses_as_context(relevant_expenses)

        # Step 3: Generate answer using LLM
        answer = await self.ollama_service.generate_rag_response(question, context)

        return answer, len(relevant_expenses)


# Singleton instance
rag_service = RAGService()
