"""
Loads configuration/secrets from environment variables (.env file).
Never hardcode API keys anywhere else in this package.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # optional — used as a fallback for both audio transcription and text classification

# Ordered Gemini text-model fallback chain. service.py walks this top to
# bottom: when a model is rate-limited or its daily cap is spent, the call
# rolls to the next one instead of failing. Order is deliberate — it's by
# free-tier request budget, not by model quality:
#
#   model                    RPM  TPM   RPD   note
#   gemini-3.1-flash-lite     15  250K  500   primary
#   gemini-3.5-flash-lite     15  250K  500   same limits, separate bucket
#   gemini-2.5-flash-lite     10  250K   20
#   gemini-3-flash             5  250K   20   not on our key as of 2026-08-21
#   gemini-2.5-flash           5  250K   20
#   gemini-3.5-flash           5  250K   20
#   gemini-3.6-flash           5  250K   20
#   gemini-3.7-flash           5  250K   20   last — already seen bursting
#
# The two lite models carry ~1000 of the ~1120 daily requests between them,
# so the six below them are a reserve for when those two are spent, not a
# path we expect to spend much time in.
#
# gemini-3-flash is kept in the list even though models.list() didn't offer it
# on our key: the chain disables an unreachable model permanently after its
# first 404, so it costs one request per process and starts working by itself
# if the key later gains access.
#
# Override with a comma-separated GEMINI_TEXT_MODELS to try a different
# order or prune models your key can't reach.
_DEFAULT_TEXT_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash",
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
]

GEMINI_TEXT_MODELS = [
    name.strip()
    for name in os.getenv("GEMINI_TEXT_MODELS", ",".join(_DEFAULT_TEXT_MODELS)).split(",")
    if name.strip()
] or list(_DEFAULT_TEXT_MODELS)

# Head of the chain. Kept as a separate name because tests/batch_classify.py
# pins a single model deliberately (a batch run must not silently change
# models mid-scoring, or the numbers mean nothing).
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", GEMINI_TEXT_MODELS[0])

GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
EMBEDDING_DIMENSIONS = 768  # locked decision — must match the backend's pgvector column size

# How long a model sits out after a quota error, when the API doesn't tell us.
# A per-minute limit clears on the next rolling window; a per-day limit needs
# to wait for Google's midnight-Pacific reset (see service.py::_next_daily_reset).
RPM_COOLDOWN_SECONDS = 60

# Reliability settings
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1.5
REQUEST_TIMEOUT_SECONDS = 20

# Wall-clock ceiling for one whole walk of the model chain. The chain exists so
# a throttled model can't stop someone lodging a complaint — but a request that
# grinds through 8 models x 3 attempts x 20s fails the same person just as
# surely, only slower. Past this budget we stop walking and let the caller take
# its safe default: a lodged, unclassified complaint beats a perfect one that
# timed out. Deliberately shorter than the sum of the parts.
CHAIN_BUDGET_SECONDS = 45

if not GEMINI_API_KEY:
    # Don't crash at import time — service.py functions will return fallback
    # responses instead, so the backend team can keep working even before
    # a key is configured. This warning just makes the reason visible.
    import warnings
    warnings.warn(
        "GEMINI_API_KEY is not set. All ai_service calls will return "
        "fallback responses until it's configured in your .env file."
    )
