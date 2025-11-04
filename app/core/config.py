from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "expense_rag_db"

    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # Dimension for all-MiniLM-L6-v2

    # API settings
    api_title: str = "Expense RAG System"
    api_version: str = "1.0.0"
    api_description: str = "RAG system for querying personal expense data using natural language"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def database_url(self) -> str:
        """Generate PostgreSQL database URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
