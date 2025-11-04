from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import expenses_router, query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting up...")
    print(f"Database URL: {settings.database_url}")
    print(f"Ollama Host: {settings.ollama_host}")
    print(f"Ollama Model: {settings.ollama_model}")

    # Initialize database (create tables)
    init_db()
    print("Database initialized!")

    yield

    # Shutdown
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses_router)
app.include_router(query_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Expense RAG System API",
        "version": settings.api_version,
        "docs": "/docs",
        "endpoints": {
            "crud": "/expenses",
            "query": "/query",
        },
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
