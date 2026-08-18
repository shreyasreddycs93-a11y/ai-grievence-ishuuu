"""
Loads configuration/secrets from environment variables (.env file).
Never hardcode API keys anywhere else in this package.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # optional — used as a fallback for both audio transcription and text classification

# Model names, kept here so they're easy to swap without touching service.py
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-flash-lite-latest")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
EMBEDDING_DIMENSIONS = 768  # locked decision — must match the backend's pgvector column size

# Reliability settings
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1.5
REQUEST_TIMEOUT_SECONDS = 20

if not GEMINI_API_KEY:
    # Don't crash at import time — service.py functions will return fallback
    # responses instead, so the backend team can keep working even before
    # a key is configured. This warning just makes the reason visible.
    import warnings
    warnings.warn(
        "GEMINI_API_KEY is not set. All ai_service calls will return "
        "fallback responses until it's configured in your .env file."
    )
