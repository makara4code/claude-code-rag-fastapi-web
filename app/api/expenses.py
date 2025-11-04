from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse,
)
from app.services.embedding import embedding_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new expense record for the authenticated user.

    **Security:** Requires authentication. Expense is automatically associated with the current user.

    Args:
        expense_data: Expense creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created expense record
    """
    # Create expense object with user_id from authenticated user
    expense = Expense(
        user_id=current_user.id,  # SECURITY: Associate with current user
        category=expense_data.category,
        amount=expense_data.amount,
        date=expense_data.date,
        description=expense_data.description,
    )

    # Generate embedding for the expense
    embedding = embedding_service.generate_embedding_for_expense(expense)
    expense.embedding = embedding.tolist()

    # Save to database
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.get("", response_model=ExpenseListResponse)
async def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[date] = Query(None, description="Filter by start date"),
    date_to: Optional[date] = Query(None, description="Filter by end date"),
    amount_min: Optional[Decimal] = Query(None, description="Filter by minimum amount"),
    amount_max: Optional[Decimal] = Query(None, description="Filter by maximum amount"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all expenses for the authenticated user with optional filtering.

    **Security:** Only returns expenses belonging to the authenticated user.

    Args:
        category: Optional category filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        amount_min: Optional minimum amount filter
        amount_max: Optional maximum amount filter
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of expense records belonging to the current user
    """
    # Build query with user_id filter - CRITICAL FOR SECURITY
    query = db.query(Expense).filter(Expense.user_id == current_user.id)

    # Apply additional filters
    if category:
        query = query.filter(Expense.category == category)
    if date_from:
        query = query.filter(Expense.date >= date_from)
    if date_to:
        query = query.filter(Expense.date <= date_to)
    if amount_min is not None:
        query = query.filter(Expense.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Expense.amount <= amount_max)

    # Get total count for this user
    total = query.count()

    # Apply pagination and execute
    expenses = query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()

    return ExpenseListResponse(total=total, expenses=expenses)


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a single expense by ID.

    **Security:** Only returns the expense if it belongs to the authenticated user.

    Args:
        expense_id: Expense ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Expense record

    Raises:
        HTTPException: If expense not found or doesn't belong to user
    """
    # SECURITY: Filter by both expense_id AND user_id
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found or access denied",
        )

    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing expense record.

    **Security:** Only allows updating expenses that belong to the authenticated user.

    Args:
        expense_id: Expense ID
        expense_data: Updated expense data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated expense record

    Raises:
        HTTPException: If expense not found or doesn't belong to user
    """
    # SECURITY: Filter by both expense_id AND user_id
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found or access denied",
        )

    # Update fields if provided
    update_data = expense_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(expense, field, value)

    # Regenerate embedding if any relevant field changed
    if any(field in update_data for field in ["category", "amount", "date", "description"]):
        embedding = embedding_service.generate_embedding_for_expense(expense)
        expense.embedding = embedding.tolist()

    db.commit()
    db.refresh(expense)

    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an expense record.

    **Security:** Only allows deleting expenses that belong to the authenticated user.

    Args:
        expense_id: Expense ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If expense not found or doesn't belong to user
    """
    # SECURITY: Filter by both expense_id AND user_id
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found or access denied",
        )

    db.delete(expense)
    db.commit()

    return None
