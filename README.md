# Expense RAG System

A RAG (Retrieval-Augmented Generation) system for querying personal expense data using natural language. Built with FastAPI, PostgreSQL (with pgvector), and Ollama 3.2.

## Features

- **CRUD API**: Full REST API for managing expense records
- **Natural Language Queries**: Ask questions about your expenses in plain English
- **Vector Search**: Semantic search using embeddings and pgvector
- **LLM Integration**: Powered by Ollama 3.2 (llama3.2 model)
- **Automatic Documentation**: Interactive API docs with Swagger UI

## Architecture

The system consists of two main components:

1. **Traditional CRUD REST API**: Standard endpoints for expense management
2. **RAG-Powered Query Interface**: Natural language question answering using LLM

### Technology Stack

- **Web Framework**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **LLM**: Ollama 3.2 (llama3.2 model)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Python**: 3.13+

## Project Structure

```
expense-rag-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── expenses.py         # CRUD endpoints
│   │   └── query.py            # RAG query endpoint
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── database.py         # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── expense.py          # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── expense.py          # Pydantic schemas for expenses
│   │   └── query.py            # Pydantic schemas for queries
│   └── services/
│       ├── __init__.py
│       ├── embedding.py        # Embedding generation
│       ├── ollama.py           # Ollama LLM integration
│       └── rag.py              # RAG service
├── scripts/
│   ├── init_db.sql             # Database initialization
│   └── seed_data.py            # Sample data seeding
├── docker-compose.yml          # Docker setup for PostgreSQL & Ollama
├── pyproject.toml              # Poetry dependencies
├── Makefile                    # Common commands
├── .env.example                # Environment variables template
└── README.md
```

## Installation

### Prerequisites

- Python 3.13+
- Docker and Docker Compose
- Poetry (Python package manager)

### Setup Steps

1. **Clone the repository**

```bash
git clone <repository-url>
cd claude-code-rag-fastapi-web
```

2. **Install Poetry (if not already installed)**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies**

```bash
make install
# or manually:
poetry install
```

4. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env if needed (default values should work)
```

5. **Start PostgreSQL and Ollama**

```bash
make db-up
# or manually:
docker-compose up -d
```

6. **Pull Ollama model**

```bash
make ollama-pull
# or manually:
docker exec expense-rag-ollama ollama pull llama3.2
```

This will download the llama3.2 model (~2GB). Wait for it to complete.

7. **Seed the database with sample data** (optional but recommended)

```bash
make seed
# or manually:
poetry run python scripts/seed_data.py
```

8. **Run the application**

```bash
make run
# or manually:
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Data Model

Each expense record includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique identifier (auto-generated) |
| `category` | String | Expense type (electric, water, groceries, rent, transportation, entertainment, etc.) |
| `amount` | Decimal | Cost (e.g., 125.50) |
| `date` | Date | Date of expense |
| `description` | String | Optional text description |
| `created_at` | DateTime | Record creation timestamp |
| `updated_at` | DateTime | Last modification timestamp |
| `embedding` | Vector | Vector embedding for semantic search (auto-generated) |

## API Endpoints

### CRUD Endpoints

#### Create Expense
```http
POST /expenses
Content-Type: application/json

{
  "category": "groceries",
  "amount": 156.89,
  "date": "2025-01-15",
  "description": "Weekly grocery shopping"
}
```

#### List Expenses (with filtering)
```http
GET /expenses?category=electric&date_from=2025-01-01&date_to=2025-03-31
```

Query parameters:
- `category`: Filter by category
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)
- `amount_min`: Minimum amount
- `amount_max`: Maximum amount
- `skip`: Pagination offset (default: 0)
- `limit`: Page size (default: 100, max: 1000)

#### Get Single Expense
```http
GET /expenses/{id}
```

#### Update Expense
```http
PUT /expenses/{id}
Content-Type: application/json

{
  "amount": 99.99,
  "description": "Updated description"
}
```

#### Delete Expense
```http
DELETE /expenses/{id}
```

### RAG Query Endpoint

#### Natural Language Query
```http
POST /query
Content-Type: application/json

{
  "question": "What were my total electric bills last quarter?"
}
```

Response:
```json
{
  "question": "What were my total electric bills last quarter?",
  "answer": "Based on your expense records, your total electric bills for the last quarter were $334.50. This includes three monthly bills: $125.50 in [date], $98.75 in [date], and $110.25 in [date].",
  "retrieved_count": 3
}
```

## Example Natural Language Queries

Here are some example questions you can ask:

1. **Totals and Summaries**
   - "What were my total electric bills last quarter?"
   - "How much did I spend on groceries in the past month?"
   - "What's my total spending on utilities?"

2. **Specific Queries**
   - "What was my highest expense last month?"
   - "Show me all expenses over $100 in the past 3 months"
   - "How much did I spend on water in January?"

3. **Averages and Patterns**
   - "What's my average monthly spending on utilities?"
   - "What's my average grocery bill?"
   - "How much do I typically spend on transportation per month?"

4. **Category-Based**
   - "List all my entertainment expenses"
   - "What did I spend on dining out?"
   - "Show me my rent payments"

## How RAG Works

The RAG (Retrieval-Augmented Generation) system works in three steps:

1. **Embedding Generation**: When an expense is created or updated, the system generates a vector embedding that captures the semantic meaning of the expense (category, amount, date, description).

2. **Semantic Search**: When you ask a question, the system:
   - Converts your question into a vector embedding
   - Searches the database for the most relevant expense records using cosine similarity
   - Retrieves the top 10 most relevant records

3. **LLM Response Generation**: The retrieved expenses are formatted as context and sent to Ollama (llama3.2) along with your question. The LLM generates a natural language answer based on the actual data.

This ensures that answers are grounded in your actual expense data and not hallucinated.

## Database Setup

### Using Docker (Recommended)

The `docker-compose.yml` file includes both PostgreSQL with pgvector and Ollama:

```bash
make db-up
```

### Manual Setup

If you prefer to set up PostgreSQL manually:

1. Install PostgreSQL 16+
2. Install pgvector extension:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install postgresql-16-pgvector

   # On macOS with Homebrew
   brew install pgvector
   ```

3. Create database and enable extension:
   ```sql
   CREATE DATABASE expense_rag_db;
   \c expense_rag_db
   CREATE EXTENSION vector;
   ```

4. Update `.env` with your database credentials

### Installing Ollama Locally

If you prefer to run Ollama locally instead of Docker:

1. Download from https://ollama.ai
2. Install the application
3. Pull the model:
   ```bash
   ollama pull llama3.2
   ```
4. Update `.env`:
   ```
   OLLAMA_HOST=http://localhost:11434
   ```

## Development

### Running Tests

```bash
make test
# or:
poetry run pytest
```

### Code Formatting

```bash
poetry run black app/
poetry run ruff check app/
```

### Database Reset

To reset the database (remove all data):

```bash
make db-reset
```

## Configuration

All configuration is managed through environment variables in `.env`:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=expense_rag_db

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show available commands |
| `make install` | Install dependencies |
| `make dev` | Install development dependencies |
| `make db-up` | Start PostgreSQL and Ollama |
| `make db-down` | Stop PostgreSQL and Ollama |
| `make db-reset` | Reset database |
| `make seed` | Seed database with sample data |
| `make run` | Run the FastAPI application |
| `make test` | Run tests |
| `make clean` | Clean temporary files |
| `make ollama-pull` | Pull llama3.2 model |

## Troubleshooting

### Ollama Connection Error

If you get "Error calling Ollama":
1. Check if Ollama is running: `docker ps` or `ollama list`
2. Verify the model is pulled: `make ollama-pull`
3. Check `OLLAMA_HOST` in `.env`

### Database Connection Error

If you get "could not connect to server":
1. Check if PostgreSQL is running: `docker ps`
2. Verify credentials in `.env`
3. Check if port 5432 is available

### Embedding Model Download

On first run, sentence-transformers will download the embedding model (~90MB). This is normal and only happens once.

## Performance Considerations

- **Embedding Generation**: Takes ~50-100ms per expense on first creation
- **Vector Search**: Very fast (<10ms) for databases with <100k records
- **LLM Response**: Depends on Ollama/hardware (typically 2-5 seconds)
- **Pagination**: Use `skip` and `limit` parameters for large result sets

## Future Enhancements

- [ ] Add authentication and user management
- [ ] Support for multiple currencies
- [ ] Expense analytics and visualizations
- [ ] Budget tracking and alerts
- [ ] Export to CSV/Excel
- [ ] Mobile app integration
- [ ] Real-time updates with WebSockets

## License

MIT License - feel free to use this project for learning or production.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.
