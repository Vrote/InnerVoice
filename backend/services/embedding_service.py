# backend/services/embedding_service.py
import logging
import httpx
from backend.core.config import settings

logger = logging.getLogger(__name__)

async def embed_text(text: str) -> list[float]:
    """
    Generate embedding vector using Groq Embeddings API.
    Model: nomic-embed-text-v1.5 (768 dimensions).
    Timeout: 15.0s.
    Fallback: 768-dimensional zero vector.
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY is not set or placeholder. Returning zero vector.")
        return [0.0] * 768

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROQ_EMBEDDING_MODEL,
                    "input": text[:8000]
                }
            )
            response.raise_for_status()
            res_json = response.json()
            return res_json["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Failed to generate embedding from Groq API: {e}")
        return [0.0] * 768
