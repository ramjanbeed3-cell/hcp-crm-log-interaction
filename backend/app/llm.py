"""
Thin wrapper around Groq-hosted models via langchain-groq.

Primary model: gemma2-9b-it  (fast, cheap, used for tool-calling loop)
Fallback / heavier reasoning: llama-3.3-70b-versatile

Create a new key at https://console.groq.com/keys and set GROQ_API_KEY in .env
"""

from langchain_groq import ChatGroq

from app.config import settings


def get_primary_llm(temperature: float = 0.2):
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,  # gemma2-9b-it
        temperature=temperature,
    )


def get_fallback_llm(temperature: float = 0.3):
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_FALLBACK_MODEL,  # llama-3.3-70b-versatile
        temperature=temperature,
    )
