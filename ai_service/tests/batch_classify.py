"""
TEST-ONLY batched classification helper for the holdout scorer.

classify_complaint() in service.py is deliberately one-complaint-at-a-time —
that matches the real production contract (a citizen submits one complaint
and needs an immediate single-complaint response back). This module exists
ONLY to get through holdout runs faster without tripping a provider's
per-day or per-minute rate limit: it sends the rubric + few-shot examples
ONCE per batch of N complaints instead of once per complaint, which cuts
Gemini's daily request count (the thing that hit its 500/day free-tier cap)
by roughly a factor of N.

Never imported by service.py. Never used in production. Operates like
run_holdout.py's "raw" mode — no translation — since translation is its own
per-case call and batching it too would need a second, separate design.

Reliability: mirrors service.py's posture. A batch call that fails outright,
or whose response can't be parsed into exactly N items, returns N error
rows rather than raising — one bad batch should never crash the whole run
or silently drop cases.
"""
import logging

from google.genai import types

from .. import config, service
from ..prompts import build_batch_classification_prompt

logger = logging.getLogger("ai_service.tests.batch_classify")


def _batch_error(reason: str) -> dict:
    result = service._fallback_classification()
    result["batch_error"] = reason
    return result


def _batch_error_rows(reason: str, n: int) -> list:
    """N independent error dicts, not N references to the same object —
    `[_batch_error(reason)] * n` would alias one dict across every row."""
    return [_batch_error(reason) for _ in range(n)]


def _extract_results(parsed, expected_n: int):
    """The batch prompt always asks for {"results": [...]} — a top-level
    JSON object, not a bare array, so this works under Groq's json_object
    response mode too (which rejects a bare top-level array). Returns the
    results list, or None if the shape doesn't match."""
    if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
        results = parsed["results"]
        if len(results) == expected_n:
            return results
    return None


def classify_batch_gemini(texts: list) -> list:
    """Classifies a batch of complaints in ONE Gemini call. Returns one
    validated classification dict per input text, same order. See module
    docstring for the reliability contract."""
    client = service._get_client()
    if client is None:
        return _batch_error_rows("no Gemini client configured", len(texts))

    prompt = build_batch_classification_prompt(texts)
    try:
        response = service._with_retry(
            client.models.generate_content,
            model=config.GEMINI_TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        parsed = service._extract_json(response.text)
    except Exception as exc:  # noqa: BLE001 — a bad batch must not kill the run
        logger.error("classify_batch_gemini: batch call failed: %s", exc)
        return _batch_error_rows(str(exc), len(texts))

    results = _extract_results(parsed, len(texts))
    if results is None:
        logger.error("classify_batch_gemini: response shape mismatch, expected %d results", len(texts))
        return _batch_error_rows(f"batch response shape mismatch (expected {len(texts)} results)", len(texts))

    return [service._validate_classification(item, source="gemini") for item in results]


def classify_batch_groq(texts: list) -> list:
    """Same contract as classify_batch_gemini(), routed to Groq instead.
    Keep batches small here — Groq's free tier is a tokens-PER-MINUTE cap
    (observed: 8000 TPM), and the static rubric+examples block alone is
    several thousand tokens, so a batch that's too large can exceed the
    limit in a single request regardless of pacing."""
    if not config.GROQ_API_KEY:
        return _batch_error_rows("no Groq API key configured", len(texts))

    prompt = build_batch_classification_prompt(texts)
    try:
        parsed = service._with_retry(_call_groq_batch, prompt)
    except Exception as exc:  # noqa: BLE001
        logger.error("classify_batch_groq: batch call failed: %s", exc)
        return _batch_error_rows(str(exc), len(texts))

    results = _extract_results(parsed, len(texts))
    if results is None:
        logger.error("classify_batch_groq: response shape mismatch, expected %d results", len(texts))
        return _batch_error_rows(f"batch response shape mismatch (expected {len(texts)} results)", len(texts))

    return [service._validate_classification(item, source="groq") for item in results]


def classify_batch(texts: list) -> list:
    """Batch-level version of service.py's Gemini -> Groq provider chain:
    tries Gemini for the whole batch, and if that call fails outright,
    retries the SAME batch on Groq rather than losing it. A batch either
    fully succeeds on a provider or fully fails (classify_batch_gemini /
    classify_batch_groq never return a partial mix), so checking the first
    result's batch_error is enough to know whether to fall back."""
    results = classify_batch_gemini(texts)
    if results and results[0].get("batch_error"):
        logger.warning("classify_batch: Gemini batch failed (%s), trying Groq batch fallback",
                        results[0]["batch_error"])
        results = classify_batch_groq(texts)
    return results


def _call_groq_batch(prompt: str) -> dict:
    from groq import Groq  # imported lazily, same convention as service.py

    client = Groq(api_key=config.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=config.GROQ_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw_text = response.choices[0].message.content
    return service._extract_json(raw_text)
