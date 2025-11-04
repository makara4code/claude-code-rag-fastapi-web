#!/usr/bin/env python3
"""
Script to seed the database with sample expense data.
Run this after setting up the database and installing dependencies.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.models.expense import Expense
from app.services.embedding import embedding_service


def create_sample_expenses():
    """Create sample expense records."""
    today = date.today()

    sample_expenses = [
        # Electric bills
        {
            "category": "electric",
            "amount": Decimal("125.50"),
            "date": today - timedelta(days=90),
            "description": "Monthly electric bill - winter heating",
        },
        {
            "category": "electric",
            "amount": Decimal("98.75"),
            "date": today - timedelta(days=60),
            "description": "Monthly electric bill - moderate usage",
        },
        {
            "category": "electric",
            "amount": Decimal("110.25"),
            "date": today - timedelta(days=30),
            "description": "Monthly electric bill - spring",
        },
        # Water bills
        {
            "category": "water",
            "amount": Decimal("45.00"),
            "date": today - timedelta(days=85),
            "description": "Monthly water bill",
        },
        {
            "category": "water",
            "amount": Decimal("52.30"),
            "date": today - timedelta(days=55),
            "description": "Monthly water bill - increased usage",
        },
        {
            "category": "water",
            "amount": Decimal("48.75"),
            "date": today - timedelta(days=25),
            "description": "Monthly water bill",
        },
        # Groceries
        {
            "category": "groceries",
            "amount": Decimal("156.89"),
            "date": today - timedelta(days=7),
            "description": "Weekly grocery shopping at Whole Foods",
        },
        {
            "category": "groceries",
            "amount": Decimal("89.42"),
            "date": today - timedelta(days=14),
            "description": "Weekly grocery shopping",
        },
        {
            "category": "groceries",
            "amount": Decimal("203.15"),
            "date": today - timedelta(days=21),
            "description": "Weekly grocery shopping - stocking up",
        },
        {
            "category": "groceries",
            "amount": Decimal("124.67"),
            "date": today - timedelta(days=28),
            "description": "Weekly grocery shopping",
        },
        # Rent
        {
            "category": "rent",
            "amount": Decimal("1850.00"),
            "date": today - timedelta(days=30),
            "description": "Monthly rent payment",
        },
        {
            "category": "rent",
            "amount": Decimal("1850.00"),
            "date": today - timedelta(days=60),
            "description": "Monthly rent payment",
        },
        {
            "category": "rent",
            "amount": Decimal("1850.00"),
            "date": today - timedelta(days=90),
            "description": "Monthly rent payment",
        },
        # Transportation
        {
            "category": "transportation",
            "amount": Decimal("65.00"),
            "date": today - timedelta(days=10),
            "description": "Gas station fill-up",
        },
        {
            "category": "transportation",
            "amount": Decimal("75.50"),
            "date": today - timedelta(days=20),
            "description": "Gas station fill-up",
        },
        {
            "category": "transportation",
            "amount": Decimal("120.00"),
            "date": today - timedelta(days=35),
            "description": "Monthly metro pass",
        },
        {
            "category": "transportation",
            "amount": Decimal("58.25"),
            "date": today - timedelta(days=45),
            "description": "Uber rides",
        },
        # Entertainment
        {
            "category": "entertainment",
            "amount": Decimal("45.99"),
            "date": today - timedelta(days=5),
            "description": "Movie tickets and snacks",
        },
        {
            "category": "entertainment",
            "amount": Decimal("89.50"),
            "date": today - timedelta(days=15),
            "description": "Concert tickets",
        },
        {
            "category": "entertainment",
            "amount": Decimal("29.99"),
            "date": today - timedelta(days=25),
            "description": "Streaming service subscriptions",
        },
        # Dining out
        {
            "category": "dining",
            "amount": Decimal("67.89"),
            "date": today - timedelta(days=3),
            "description": "Dinner at Italian restaurant",
        },
        {
            "category": "dining",
            "amount": Decimal("45.23"),
            "date": today - timedelta(days=8),
            "description": "Lunch meeting",
        },
        {
            "category": "dining",
            "amount": Decimal("123.45"),
            "date": today - timedelta(days=12),
            "description": "Birthday dinner celebration",
        },
        {
            "category": "dining",
            "amount": Decimal("38.90"),
            "date": today - timedelta(days=18),
            "description": "Weekend brunch",
        },
    ]

    return sample_expenses


def seed_database():
    """Seed the database with sample data."""
    print("Initializing database...")
    init_db()

    print("Creating database session...")
    db = SessionLocal()

    try:
        # Check if database already has data
        existing_count = db.query(Expense).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} expense records.")
            response = input("Do you want to add more sample data anyway? (y/n): ")
            if response.lower() != "y":
                print("Aborting seed operation.")
                return

        print("Creating sample expenses...")
        sample_expenses = create_sample_expenses()

        for expense_data in sample_expenses:
            expense = Expense(**expense_data)

            # Generate embedding
            print(f"Generating embedding for: {expense.category} - ${expense.amount}")
            embedding = embedding_service.generate_embedding_for_expense(expense)
            expense.embedding = embedding.tolist()

            db.add(expense)

        db.commit()
        print(f"\n✓ Successfully seeded {len(sample_expenses)} expense records!")

        # Display summary
        total = db.query(Expense).count()
        print(f"\nDatabase now contains {total} total expense records.")

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Expense RAG System - Database Seeding Script")
    print("=" * 60)
    print()

    try:
        seed_database()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
