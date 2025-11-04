.PHONY: help install dev db-up db-down db-reset seed run test clean

help:
	@echo "Expense RAG System - Makefile Commands"
	@echo "======================================"
	@echo "install      - Install dependencies using poetry"
	@echo "dev          - Install development dependencies"
	@echo "db-up        - Start PostgreSQL and Ollama using docker-compose"
	@echo "db-down      - Stop PostgreSQL and Ollama"
	@echo "db-reset     - Reset database (remove all data)"
	@echo "seed         - Seed database with sample data"
	@echo "run          - Run the FastAPI application"
	@echo "test         - Run tests"
	@echo "clean        - Clean up temporary files"
	@echo "ollama-pull  - Pull the llama3.2 model for Ollama"

install:
	poetry install --no-dev

dev:
	poetry install

db-up:
	docker-compose up -d
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	@echo "Database is ready!"

db-down:
	docker-compose down

db-reset:
	docker-compose down -v
	docker-compose up -d
	@echo "Database has been reset!"

seed:
	poetry run python scripts/seed_data.py

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} +

ollama-pull:
	docker exec expense-rag-ollama ollama pull llama3.2
	@echo "Ollama model llama3.2 has been pulled!"
