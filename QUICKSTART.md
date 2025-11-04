# Quick Start Guide

Get the Expense RAG System running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Python 3.13+ installed
- Poetry installed (or use pip with requirements.txt)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd claude-code-rag-fastapi-web
```

### 2. Install Dependencies

Using Poetry (recommended):
```bash
poetry install
```

Or using pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

The default values work out of the box!

### 4. Start Services

```bash
# Start PostgreSQL and Ollama
docker-compose up -d

# Wait ~10 seconds for services to start
sleep 10

# Pull the Ollama model (this will take a few minutes, ~2GB download)
docker exec expense-rag-ollama ollama pull llama3.2
```

### 5. Seed Sample Data (Optional)

```bash
poetry run python scripts/seed_data.py
# or with pip: python scripts/seed_data.py
```

### 6. Run the Application

Using Poetry:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or with Make:
```bash
make run
```

### 7. Test It Out!

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

## First API Calls

### Create an Expense

```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "groceries",
    "amount": 156.89,
    "date": "2025-01-15",
    "description": "Weekly grocery shopping"
  }'
```

### Ask a Question

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How much did I spend on groceries?"
  }'
```

### List Expenses

```bash
curl "http://localhost:8000/expenses"
```

## Using the Interactive Docs

Navigate to http://localhost:8000/docs for a full interactive API documentation where you can:
- Try out all endpoints
- See request/response schemas
- Test the RAG query system

## Troubleshooting

**Ollama not responding?**
```bash
# Check if Ollama container is running
docker ps | grep ollama

# Check Ollama logs
docker logs expense-rag-ollama

# Verify model is pulled
docker exec expense-rag-ollama ollama list
```

**Database connection error?**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs expense-rag-postgres
```

**Port already in use?**
```bash
# Change the port in the run command
poetry run uvicorn app.main:app --reload --port 8001
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Try the example queries in the README
- Explore the API documentation at http://localhost:8000/docs
- Add your own expense data
- Experiment with natural language queries

## Stopping Services

```bash
# Stop the API (Ctrl+C in the terminal)

# Stop Docker services
docker-compose down

# To completely remove data
docker-compose down -v
```

Enjoy your Expense RAG System! 🚀
