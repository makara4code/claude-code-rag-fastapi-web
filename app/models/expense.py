from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.core.config import settings


class Expense(Base):
    """Expense database model."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Vector embedding for RAG functionality
    embedding = Column(Vector(settings.embedding_dimension), nullable=True)

    def __repr__(self):
        return f"<Expense(id={self.id}, category={self.category}, amount={self.amount}, date={self.date})>"
