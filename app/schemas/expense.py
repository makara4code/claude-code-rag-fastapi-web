from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ExpenseBase(BaseModel):
    """Base schema for Expense."""

    category: str = Field(..., min_length=1, max_length=100, description="Expense category")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Expense amount")
    date: date = Field(..., description="Date of expense")
    description: Optional[str] = Field(None, description="Optional description")


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense."""

    pass


class ExpenseUpdate(BaseModel):
    """Schema for updating an existing expense."""

    category: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    date: Optional[date] = None
    description: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    """Schema for expense response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    """Schema for list of expenses."""

    total: int
    expenses: list[ExpenseResponse]


class ExpenseFilter(BaseModel):
    """Schema for filtering expenses."""

    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
