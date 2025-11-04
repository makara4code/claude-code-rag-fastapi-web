# API Examples

This document provides practical examples for all API endpoints.

## Base URL

```
http://localhost:8000
```

## CRUD Endpoints

### 1. Create Expense

**Endpoint:** `POST /expenses`

**Example 1: Electric Bill**
```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "electric",
    "amount": 125.50,
    "date": "2025-01-15",
    "description": "Monthly electric bill"
  }'
```

**Example 2: Grocery Shopping**
```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "groceries",
    "amount": 89.99,
    "date": "2025-01-20",
    "description": "Weekly grocery shopping at Whole Foods"
  }'
```

**Example 3: Water Bill**
```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "water",
    "amount": 45.00,
    "date": "2025-01-10",
    "description": "Monthly water bill"
  }'
```

**Response:**
```json
{
  "id": 1,
  "category": "electric",
  "amount": 125.50,
  "date": "2025-01-15",
  "description": "Monthly electric bill",
  "created_at": "2025-01-25T10:30:00",
  "updated_at": "2025-01-25T10:30:00"
}
```

### 2. List All Expenses

**Endpoint:** `GET /expenses`

**Example 1: List all expenses**
```bash
curl "http://localhost:8000/expenses"
```

**Example 2: Filter by category**
```bash
curl "http://localhost:8000/expenses?category=electric"
```

**Example 3: Filter by date range**
```bash
curl "http://localhost:8000/expenses?date_from=2025-01-01&date_to=2025-01-31"
```

**Example 4: Filter by amount range**
```bash
curl "http://localhost:8000/expenses?amount_min=50&amount_max=150"
```

**Example 5: Combined filters with pagination**
```bash
curl "http://localhost:8000/expenses?category=groceries&date_from=2025-01-01&skip=0&limit=10"
```

**Response:**
```json
{
  "total": 25,
  "expenses": [
    {
      "id": 1,
      "category": "electric",
      "amount": 125.50,
      "date": "2025-01-15",
      "description": "Monthly electric bill",
      "created_at": "2025-01-25T10:30:00",
      "updated_at": "2025-01-25T10:30:00"
    },
    ...
  ]
}
```

### 3. Get Single Expense

**Endpoint:** `GET /expenses/{id}`

```bash
curl "http://localhost:8000/expenses/1"
```

**Response:**
```json
{
  "id": 1,
  "category": "electric",
  "amount": 125.50,
  "date": "2025-01-15",
  "description": "Monthly electric bill",
  "created_at": "2025-01-25T10:30:00",
  "updated_at": "2025-01-25T10:30:00"
}
```

### 4. Update Expense

**Endpoint:** `PUT /expenses/{id}`

**Example 1: Update amount**
```bash
curl -X PUT "http://localhost:8000/expenses/1" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 130.00
  }'
```

**Example 2: Update multiple fields**
```bash
curl -X PUT "http://localhost:8000/expenses/1" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 130.00,
    "description": "Monthly electric bill - corrected amount"
  }'
```

**Response:**
```json
{
  "id": 1,
  "category": "electric",
  "amount": 130.00,
  "date": "2025-01-15",
  "description": "Monthly electric bill - corrected amount",
  "created_at": "2025-01-25T10:30:00",
  "updated_at": "2025-01-25T11:00:00"
}
```

### 5. Delete Expense

**Endpoint:** `DELETE /expenses/{id}`

```bash
curl -X DELETE "http://localhost:8000/expenses/1"
```

**Response:** `204 No Content`

## RAG Query Endpoint

### Natural Language Queries

**Endpoint:** `POST /query`

**Example 1: Total spending by category**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What were my total electric bills last quarter?"
  }'
```

**Response:**
```json
{
  "question": "What were my total electric bills last quarter?",
  "answer": "Based on your expense records, your total electric bills for the last quarter were $334.50. This includes three monthly bills: $125.50 in November, $98.75 in December, and $110.25 in January.",
  "retrieved_count": 3
}
```

**Example 2: Spending in a specific month**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How much did I spend on water in January?"
  }'
```

**Example 3: Highest expense**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What was my highest expense last month?"
  }'
```

**Example 4: Expenses above threshold**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all expenses over $100 in the past 3 months"
  }'
```

**Example 5: Average spending**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is my average monthly spending on utilities?"
  }'
```

**Example 6: Category comparison**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Do I spend more on groceries or dining out?"
  }'
```

**Example 7: Spending trends**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How has my grocery spending changed over the last few months?"
  }'
```

**Example 8: Total by category**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are my total transportation costs?"
  }'
```

## Health Check

**Endpoint:** `GET /health`

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy"
}
```

## Root Endpoint

**Endpoint:** `GET /`

```bash
curl "http://localhost:8000/"
```

**Response:**
```json
{
  "message": "Welcome to the Expense RAG System API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "crud": "/expenses",
    "query": "/query"
  }
}
```

## Python Examples

### Using `requests` library

```python
import requests

# Create expense
response = requests.post(
    "http://localhost:8000/expenses",
    json={
        "category": "electric",
        "amount": 125.50,
        "date": "2025-01-15",
        "description": "Monthly electric bill"
    }
)
print(response.json())

# Query expenses
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "What were my total electric bills last quarter?"
    }
)
print(response.json())

# List expenses with filters
response = requests.get(
    "http://localhost:8000/expenses",
    params={
        "category": "electric",
        "date_from": "2025-01-01",
        "date_to": "2025-03-31"
    }
)
print(response.json())
```

### Using `httpx` library (async)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Create expense
        response = await client.post(
            "http://localhost:8000/expenses",
            json={
                "category": "groceries",
                "amount": 89.99,
                "date": "2025-01-20",
                "description": "Weekly shopping"
            }
        )
        print(response.json())

        # Query expenses
        response = await client.post(
            "http://localhost:8000/query",
            json={
                "question": "How much did I spend on groceries?"
            }
        )
        print(response.json())

asyncio.run(main())
```

## JavaScript Examples

### Using `fetch` API

```javascript
// Create expense
fetch('http://localhost:8000/expenses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    category: 'electric',
    amount: 125.50,
    date: '2025-01-15',
    description: 'Monthly electric bill'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Query expenses
fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What were my total electric bills last quarter?'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Using `axios`

```javascript
const axios = require('axios');

// Create expense
axios.post('http://localhost:8000/expenses', {
  category: 'groceries',
  amount: 89.99,
  date: '2025-01-20',
  description: 'Weekly shopping'
})
.then(response => console.log(response.data));

// Query expenses
axios.post('http://localhost:8000/query', {
  question: 'How much did I spend on groceries?'
})
.then(response => console.log(response.data));
```

## Interactive Documentation

For a more interactive experience, visit the auto-generated API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Full schema documentation
- Request/response examples
- Authentication testing (when implemented)
