from typing import Optional
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings
from app.models.expense import Expense


class EmbeddingService:
    """Service for generating embeddings for expense records."""

    def __init__(self):
        """Initialize the embedding model."""
        self.model = SentenceTransformer(settings.embedding_model)

    def generate_text_for_expense(self, expense: Expense) -> str:
        """
        Generate searchable text representation of an expense.

        Args:
            expense: Expense object

        Returns:
            Text representation combining all relevant fields
        """
        parts = [
            f"Category: {expense.category}",
            f"Amount: ${expense.amount}",
            f"Date: {expense.date.strftime('%Y-%m-%d')}",
        ]

        if expense.description:
            parts.append(f"Description: {expense.description}")

        return " | ".join(parts)

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for given text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def generate_embedding_for_expense(self, expense: Expense) -> np.ndarray:
        """
        Generate embedding for an expense record.

        Args:
            expense: Expense object

        Returns:
            Embedding vector as numpy array
        """
        text = self.generate_text_for_expense(expense)
        return self.generate_embedding(text)

    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query.

        Args:
            query: Search query text

        Returns:
            Embedding vector as numpy array
        """
        return self.generate_embedding(query)


# Singleton instance
embedding_service = EmbeddingService()
