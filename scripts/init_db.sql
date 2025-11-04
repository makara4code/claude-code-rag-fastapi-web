-- Initialize database for Expense RAG System
-- This script sets up the database with pgvector extension

-- Create the database (run this as postgres superuser)
-- CREATE DATABASE expense_rag_db;

-- Connect to the database
\c expense_rag_db

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE expense_rag_db TO postgres;

-- Create schema if needed
-- CREATE SCHEMA IF NOT EXISTS public;
-- GRANT ALL ON SCHEMA public TO postgres;
-- GRANT ALL ON SCHEMA public TO public;

-- Note: Tables will be created automatically by SQLAlchemy when the application starts
-- The Expense table will include a vector column for embeddings
