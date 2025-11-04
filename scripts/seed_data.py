#!/usr/bin/env python3
"""
Script to seed the database with sample users and expense data.
Run this after setting up the database and installing dependencies.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.expense import Expense
from app.services.embedding import embedding_service


def create_test_users(db):
    """Create test user accounts."""
    users = [
        {
            "email": "alice@example.com",
            "username": "alice",
            "password": "TestPass123",
            "full_name": "Alice Smith",
        },
        {
            "email": "bob@example.com",
            "username": "bob",
            "password": "TestPass456",
            "full_name": "Bob Johnson",
        },
    ]

    created_users = []
    for user_data in users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()

        if existing_user:
            print(f"User '{user_data['username']}' already exists, skipping...")
            created_users.append(existing_user)
            continue

        # Create new user
        hashed_password = get_password_hash(user_data["password"])
        new_user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            is_active=True,
            is_superuser=False,
        )

        db.add(new_user)
        db.flush()  # Get the user ID
        print(f"✓ Created user: {user_data['username']} (ID: {new_user.id})")
        created_users.append(new_user)

    db.commit()
    return created_users


def create_sample_expenses_for_user(user_id, username):
    """Create sample expense records for a specific user."""
    today = date.today()

    # Customize expenses per user
    if username == "alice":
        sample_expenses = [
            # Alice's expenses - moderate spending
            {
                "user_id": user_id,
                "category": "electric",
                "amount": Decimal("125.50"),
                "date": today - timedelta(days=90),
                "description": "Monthly electric bill - winter heating",
            },
            {
                "user_id": user_id,
                "category": "electric",
                "amount": Decimal("98.75"),
                "date": today - timedelta(days=60),
                "description": "Monthly electric bill - moderate usage",
            },
            {
                "user_id": user_id,
                "category": "electric",
                "amount": Decimal("110.25"),
                "date": today - timedelta(days=30),
                "description": "Monthly electric bill - spring",
            },
            {
                "user_id": user_id,
                "category": "water",
                "amount": Decimal("45.00"),
                "date": today - timedelta(days=85),
                "description": "Monthly water bill",
            },
            {
                "user_id": user_id,
                "category": "water",
                "amount": Decimal("52.30"),
                "date": today - timedelta(days=55),
                "description": "Monthly water bill - increased usage",
            },
            {
                "user_id": user_id,
                "category": "water",
                "amount": Decimal("48.75"),
                "date": today - timedelta(days=25),
                "description": "Monthly water bill",
            },
            {
                "user_id": user_id,
                "category": "groceries",
                "amount": Decimal("156.89"),
                "date": today - timedelta(days=7),
                "description": "Weekly grocery shopping at Whole Foods",
            },
            {
                "user_id": user_id,
                "category": "groceries",
                "amount": Decimal("89.42"),
                "date": today - timedelta(days=14),
                "description": "Weekly grocery shopping",
            },
            {
                "user_id": user_id,
                "category": "rent",
                "amount": Decimal("1500.00"),
                "date": today - timedelta(days=30),
                "description": "Monthly rent payment",
            },
            {
                "user_id": user_id,
                "category": "transportation",
                "amount": Decimal("65.00"),
                "date": today - timedelta(days=10),
                "description": "Gas station fill-up",
            },
            {
                "user_id": user_id,
                "category": "entertainment",
                "amount": Decimal("45.99"),
                "date": today - timedelta(days=5),
                "description": "Movie tickets and snacks",
            },
            {
                "user_id": user_id,
                "category": "dining",
                "amount": Decimal("67.89"),
                "date": today - timedelta(days=3),
                "description": "Dinner at Italian restaurant",
            },
        ]
    else:  # bob
        sample_expenses = [
            # Bob's expenses - different pattern
            {
                "user_id": user_id,
                "category": "electric",
                "amount": Decimal("145.00"),
                "date": today - timedelta(days=88),
                "description": "Electric bill - larger apartment",
            },
            {
                "user_id": user_id,
                "category": "electric",
                "amount": Decimal("132.50"),
                "date": today - timedelta(days=58),
                "description": "Electric bill - home office usage",
            },
            {
                "user_id": user_id,
                "category": "water",
                "amount": Decimal("38.00"),
                "date": today - timedelta(days=82),
                "description": "Water bill - lower usage",
            },
            {
                "user_id": user_id,
                "category": "groceries",
                "amount": Decimal("203.15"),
                "date": today - timedelta(days=21),
                "description": "Costco bulk shopping",
            },
            {
                "user_id": user_id,
                "category": "groceries",
                "amount": Decimal("124.67"),
                "date": today - timedelta(days=28),
                "description": "Weekly grocery run",
            },
            {
                "user_id": user_id,
                "category": "rent",
                "amount": Decimal("2000.00"),
                "date": today - timedelta(days=30),
                "description": "Monthly rent - downtown apartment",
            },
            {
                "user_id": user_id,
                "category": "transportation",
                "amount": Decimal("120.00"),
                "date": today - timedelta(days=35),
                "description": "Monthly metro pass",
            },
            {
                "user_id": user_id,
                "category": "transportation",
                "amount": Decimal("75.50"),
                "date": today - timedelta(days=20),
                "description": "Gas for weekend trip",
            },
            {
                "user_id": user_id,
                "category": "entertainment",
                "amount": Decimal("89.50"),
                "date": today - timedelta(days=15),
                "description": "Concert tickets",
            },
            {
                "user_id": user_id,
                "category": "dining",
                "amount": Decimal("123.45"),
                "date": today - timedelta(days=12),
                "description": "Birthday dinner celebration",
            },
            {
                "user_id": user_id,
                "category": "dining",
                "amount": Decimal("38.90"),
                "date": today - timedelta(days=18),
                "description": "Weekend brunch",
            },
        ]

    return sample_expenses


def seed_database():
    """Seed the database with sample data."""
    print("=" * 60)
    print("Expense RAG System - Database Seeding Script")
    print("=" * 60)
    print()

    print("Initializing database...")
    init_db()

    print("Creating database session...")
    db = SessionLocal()

    try:
        # Create test users
        print("\nCreating test users...")
        users = create_test_users(db)

        print(f"\nTest Users Created:")
        print("-" * 60)
        for user in users:
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Password: TestPass123 or TestPass456")
            print(f"  ID: {user.id}")
            print()

        # Check if expenses already exist
        for user in users:
            existing_count = db.query(Expense).filter(Expense.user_id == user.id).count()
            if existing_count > 0:
                print(f"User '{user.username}' already has {existing_count} expenses.")
                response = input(f"Add more expenses for {user.username}? (y/n): ")
                if response.lower() != "y":
                    continue

            # Create expenses for each user
            print(f"\nCreating sample expenses for {user.username}...")
            sample_expenses = create_sample_expenses_for_user(user.id, user.username)

            for expense_data in sample_expenses:
                expense = Expense(**expense_data)

                # Generate embedding
                print(
                    f"  ✓ {expense.category} - ${expense.amount} ({expense.date.strftime('%Y-%m-%d')})"
                )
                embedding = embedding_service.generate_embedding_for_expense(expense)
                expense.embedding = embedding.tolist()

                db.add(expense)

            db.commit()
            print(f"\n✓ Successfully seeded {len(sample_expenses)} expenses for {user.username}!")

        # Display summary
        print("\n" + "=" * 60)
        print("Seeding Complete!")
        print("=" * 60)
        print("\nDatabase Summary:")
        for user in users:
            expense_count = db.query(Expense).filter(Expense.user_id == user.id).count()
            print(f"  {user.username}: {expense_count} expenses")

        print("\n" + "=" * 60)
        print("Test Accounts:")
        print("=" * 60)
        print("\n1. Alice's Account:")
        print("   Username: alice")
        print("   Email: alice@example.com")
        print("   Password: TestPass123")
        print("\n2. Bob's Account:")
        print("   Username: bob")
        print("   Email: bob@example.com")
        print("   Password: TestPass456")
        print("\n" + "=" * 60)
        print("Ready to test! Try logging in with either account.")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed_database()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
