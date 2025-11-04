# Architecture Overview

This document provides a detailed overview of the Expense RAG System architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (HTTP Clients, Web Browsers, Mobile Apps, CLI tools)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints Layer                                      │  │
│  │  ┌────────────────┐  ┌────────────────────────────────┐  │  │
│  │  │ CRUD Endpoints │  │  RAG Query Endpoint            │  │  │
│  │  │ /expenses      │  │  /query                        │  │  │
│  │  └────────┬───────┘  └────────────┬───────────────────┘  │  │
│  └───────────┼──────────────────────┼──────────────────────┘  │
│              │                      │                          │
│              ▼                      ▼                          │
│  ┌───────────────────────────────────────────────────────────┐│
│  │  Services Layer                                            ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   ││
│  │  │  Embedding   │  │    Ollama    │  │     RAG      │   ││
│  │  │   Service    │  │   Service    │  │   Service    │   ││
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   ││
│  └─────────┼──────────────────┼──────────────────┼──────────┘│
└────────────┼──────────────────┼──────────────────┼───────────┘
             │                  │                  │
             ▼                  ▼                  │
┌─────────────────────┐  ┌─────────────────────┐  │
│  sentence-          │  │   Ollama (LLM)      │  │
│  transformers       │  │   llama3.2          │  │
│  (Embeddings)       │  │                     │  │
└─────────────────────┘  └─────────────────────┘  │
                                                   │
             ┌─────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database (with pgvector)                     │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Expenses Table                                     │  │  │
│  │  │  - id (Primary Key)                                 │  │  │
│  │  │  - category, amount, date, description              │  │  │
│  │  │  - created_at, updated_at                           │  │  │
│  │  │  - embedding (Vector column)                        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Application Layer

**Purpose:** HTTP request handling and API routing

**Key Files:**
- `app/main.py`: Application entry point
- `app/api/expenses.py`: CRUD endpoints
- `app/api/query.py`: RAG query endpoint

**Responsibilities:**
- Request validation using Pydantic schemas
- Response serialization
- Error handling
- CORS configuration
- API documentation generation

### 2. Services Layer

#### 2.1 Embedding Service

**File:** `app/services/embedding.py`

**Purpose:** Generate vector embeddings for expense records

**Key Functions:**
- `generate_text_for_expense()`: Convert expense to searchable text
- `generate_embedding()`: Create vector embedding from text
- `generate_embedding_for_expense()`: Generate embedding for expense record
- `generate_query_embedding()`: Generate embedding for search query

**Model Used:** `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Fast inference (~50-100ms)
- Good for semantic similarity

#### 2.2 Ollama Service

**File:** `app/services/ollama.py`

**Purpose:** Interface with Ollama LLM for text generation

**Key Functions:**
- `generate()`: Basic text generation
- `generate_rag_response()`: RAG-specific response generation

**Model Used:** `llama3.2`
- Local inference
- Context-aware responses
- Configurable temperature

#### 2.3 RAG Service

**File:** `app/services/rag.py`

**Purpose:** Orchestrate retrieval and generation for RAG queries

**Key Functions:**
- `search_similar_expenses()`: Vector similarity search
- `format_expenses_as_context()`: Format retrieved data for LLM
- `answer_question()`: End-to-end RAG pipeline

**Workflow:**
1. Convert user question to embedding
2. Search for similar expense records (vector similarity)
3. Format top-K results as context
4. Send to LLM with question
5. Return generated answer

### 3. Data Models

#### 3.1 Database Model

**File:** `app/models/expense.py`

**ORM:** SQLAlchemy

**Table Structure:**
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    embedding VECTOR(384)
);

CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_embedding ON expenses USING ivfflat (embedding vector_cosine_ops);
```

#### 3.2 Pydantic Schemas

**Files:**
- `app/schemas/expense.py`: Expense request/response models
- `app/schemas/query.py`: Query request/response models

**Purpose:**
- Request validation
- Response serialization
- API documentation
- Type safety

### 4. Configuration Management

**File:** `app/core/config.py`

**Features:**
- Environment variable loading
- Type-safe configuration
- Default values
- Database URL generation

**Configuration Sources:**
1. Environment variables
2. `.env` file
3. Default values in code

### 5. Database Layer

**PostgreSQL with pgvector Extension**

**Vector Index:** IVFFlat (Inverted File with Flat compression)
- Good balance between speed and accuracy
- Suitable for 10K-1M vectors
- Cosine distance metric

**Query Example:**
```sql
SELECT * FROM expenses
WHERE embedding IS NOT NULL
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;
```

## Data Flow

### CRUD Operations Flow

```
┌──────────┐    POST /expenses    ┌─────────────┐
│  Client  │ ───────────────────> │   FastAPI   │
└──────────┘                      └──────┬──────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │ Validate with        │
                              │ Pydantic Schema      │
                              └──────────┬───────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │ Generate Embedding   │
                              │ (Embedding Service)  │
                              └──────────┬───────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │ Save to Database     │
                              │ (SQLAlchemy)         │
                              └──────────┬───────────┘
                                         │
                                         ▼
┌──────────┐      Response      ┌─────────────┐
│  Client  │ <───────────────── │   FastAPI   │
└──────────┘                    └─────────────┘
```

### RAG Query Flow

```
┌──────────┐    POST /query      ┌─────────────┐
│  Client  │ ───────────────────> │   FastAPI   │
│          │                      │             │
│ Question:│                      │   /query    │
│ "What    │                      │  endpoint   │
│ were my  │                      └──────┬──────┘
│ electric │                             │
│ bills?"  │                             ▼
└──────────┘              ┌───────────────────────────┐
                          │ RAG Service               │
                          └───────────┬───────────────┘
                                      │
                          ┌───────────▼────────────────┐
                          │ Step 1: Generate Query     │
                          │ Embedding                  │
                          │ (Embedding Service)        │
                          └───────────┬────────────────┘
                                      │
                          ┌───────────▼────────────────┐
                          │ Step 2: Vector Search      │
                          │ - Query database           │
                          │ - Get top 10 similar       │
                          │   expense records          │
                          │ (PostgreSQL + pgvector)    │
                          └───────────┬────────────────┘
                                      │
                          ┌───────────▼────────────────┐
                          │ Step 3: Format Context     │
                          │ - Convert expenses to text │
                          │ - Structure for LLM        │
                          └───────────┬────────────────┘
                                      │
                          ┌───────────▼────────────────┐
                          │ Step 4: Generate Answer    │
                          │ - Send context + question  │
                          │ - Get natural language     │
                          │   response                 │
                          │ (Ollama Service)           │
                          └───────────┬────────────────┘
                                      │
┌──────────┐      Response           │
│  Client  │ <───────────────────────┘
│          │
│ Answer:  │   {
│ "Your    │     "question": "...",
│ total    │     "answer": "Your total electric
│ electric │                bills were $334.50...",
│ bills    │     "retrieved_count": 3
│ were     │   }
│ $334.50" │
└──────────┘
```

## Vector Similarity Search

### Cosine Similarity

The system uses cosine similarity to find relevant expenses:

```
similarity = (A · B) / (||A|| * ||B||)

Where:
- A = query embedding vector
- B = expense embedding vector
- · = dot product
- || || = vector magnitude
```

**Why Cosine Similarity?**
- Measures semantic similarity, not magnitude
- Works well for text embeddings
- Fast computation with pgvector
- Scale-invariant

### pgvector Operator

```sql
<=> -- cosine distance (1 - cosine_similarity)
```

Lower distance = higher similarity

## Performance Characteristics

### Latency Breakdown

Typical RAG query (~3-5 seconds total):

```
Component                  Time        Percentage
─────────────────────────────────────────────────
Query embedding            ~50ms       ~1%
Vector search              ~10ms       ~0.3%
LLM generation             ~3-4s       ~98%
Response formatting        ~5ms        ~0.1%
```

**Bottleneck:** LLM inference time (depends on hardware)

### Optimization Opportunities

1. **Caching:**
   - Cache frequent queries
   - Cache embeddings
   - Implement query result cache

2. **Batch Processing:**
   - Generate embeddings in batches
   - Batch database inserts

3. **Indexing:**
   - Add more database indexes
   - Tune pgvector index parameters

4. **Async Processing:**
   - Already using async for Ollama calls
   - Consider background embedding generation

## Security Considerations

### Current State

- No authentication/authorization
- No rate limiting
- No input sanitization beyond Pydantic validation
- Database credentials in `.env`

### Production Recommendations

1. **Authentication:**
   - Add JWT-based auth
   - User management
   - API keys for programmatic access

2. **Authorization:**
   - User-specific expense records
   - Role-based access control

3. **Rate Limiting:**
   - Limit RAG queries (expensive)
   - CRUD endpoint throttling

4. **Input Validation:**
   - SQL injection protection (SQLAlchemy provides this)
   - LLM prompt injection protection
   - Max query length limits

5. **Secrets Management:**
   - Use environment variables (already done)
   - Consider vault services (AWS Secrets Manager, etc.)

## Scaling Considerations

### Vertical Scaling

- More CPU for LLM inference
- More RAM for embedding model
- Faster disk for database

### Horizontal Scaling

**Stateless API:**
- FastAPI app can run multiple instances
- Load balancer (nginx, traefik)

**Database:**
- Read replicas for queries
- Connection pooling (already in SQLAlchemy)

**Ollama:**
- Multiple Ollama instances
- Load balance LLM requests

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| CRUD latency | <100ms | ~50ms |
| Vector search | <50ms | ~10ms |
| RAG query (end-to-end) | <5s | ~3-5s |
| Throughput (CRUD) | >100 req/s | ~200 req/s |
| Throughput (RAG) | >10 req/s | ~5 req/s |

## Technology Choices

### Why FastAPI?

- Async support (important for LLM calls)
- Automatic API documentation
- Type safety with Pydantic
- High performance
- Modern Python features

### Why pgvector?

- Native PostgreSQL extension
- No separate vector database needed
- ACID guarantees
- Familiar SQL interface
- Good performance for <1M vectors

### Why Ollama?

- Local inference (privacy)
- No API costs
- Easy setup
- Multiple model support
- Good performance on consumer hardware

### Why sentence-transformers?

- Fast inference
- Good quality embeddings
- Wide model selection
- Easy to use
- Active community

## Monitoring and Observability

### Recommended Additions

1. **Logging:**
   - Structured logging (JSON)
   - Log aggregation (ELK stack)
   - Query logs for debugging

2. **Metrics:**
   - Prometheus metrics
   - Grafana dashboards
   - RAG query success rate
   - Latency percentiles

3. **Tracing:**
   - OpenTelemetry
   - Distributed tracing
   - LLM call traces

4. **Health Checks:**
   - Database connectivity
   - Ollama availability
   - Disk space
   - Memory usage

## Future Enhancements

1. **Multi-tenancy:** Support multiple users with isolated data
2. **Advanced RAG:** Implement multi-hop reasoning, query planning
3. **Caching:** Query result caching, embedding caching
4. **Analytics:** Built-in expense analytics and visualizations
5. **Export:** CSV, Excel, PDF reports
6. **Mobile:** React Native or Flutter app
7. **Real-time:** WebSocket support for live updates
8. **ML Features:** Expense categorization, anomaly detection

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Ollama Documentation](https://ollama.ai/docs)
- [sentence-transformers](https://www.sbert.net/)
- [RAG Overview](https://arxiv.org/abs/2005.11401)
