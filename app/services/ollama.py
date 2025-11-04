import httpx
from typing import Optional

from app.core.config import settings


class OllamaService:
    """Service for interacting with Ollama LLM."""

    def __init__(self):
        """Initialize Ollama service."""
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model

    async def generate(
        self, prompt: str, system: Optional[str] = None, temperature: float = 0.7
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: User prompt
            system: Optional system prompt
            temperature: Temperature for generation (0.0 to 1.0)

        Returns:
            Generated text response
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except httpx.HTTPError as e:
                raise Exception(f"Error calling Ollama: {str(e)}")

    async def generate_rag_response(self, question: str, context: str) -> str:
        """
        Generate a response using RAG (Retrieval-Augmented Generation).

        Args:
            question: User's question
            context: Retrieved context from expense records

        Returns:
            Generated answer
        """
        system_prompt = """You are a helpful financial assistant that answers questions about personal expenses.
You will be provided with relevant expense records as context.
Always base your answers on the provided context and include specific data points.
If you need to perform calculations (like totals or averages), do them accurately.
If the context doesn't contain enough information to answer the question, say so clearly.
Format monetary values with dollar signs and two decimal places."""

        user_prompt = f"""Context (Relevant Expense Records):
{context}

Question: {question}

Please provide a detailed answer based on the expense records above. Include specific amounts, dates, and categories when relevant."""

        return await self.generate(user_prompt, system=system_prompt, temperature=0.3)


# Singleton instance
ollama_service = OllamaService()
