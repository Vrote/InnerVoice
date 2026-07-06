# backend/services/llm_service.py
import logging
import asyncio
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.core.config import settings

logger = logging.getLogger(__name__)

async def run_llq_call(prompt: str, orchestrator: bool = False, json_mode: bool = True) -> str:
    """
    Call Groq LLM API with timeout and fallback handling.
    orchestrator=True uses llama3-70b-8192 (high reasoning).
    orchestrator=False uses llama3-8b-8192 (faster, cheaper tools).
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY is not set or placeholder. Returning fallback JSON/text.")
        if json_mode:
            return "{}"
        return "GROQ API Key is missing. Please configure it in the .env file."

    model_name = settings.GROQ_ORCHESTRATOR_MODEL if orchestrator else settings.GROQ_TOOL_MODEL
    
    try:
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            # Ensure the lowercase word 'json' is explicitly in the prompt text
            if "json" not in prompt.lower():
                prompt += "\n\nReturn response in json format."
            else:
                prompt += "\n\n(output must be valid json)"

        chat = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=model_name,
            temperature=0.2 if not orchestrator else 0.5,
            timeout=30.0,
            **kwargs
        )
        
        # Run in a separate thread if the invoke method is blocking, or use ainvoke
        response = await chat.ainvoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        logger.error(f"Error calling Groq model {model_name}: {e}")
        if json_mode:
            return "{}"
        raise e
