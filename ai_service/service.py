"""
Phase 1 of the AI/ML layer for GrievanceAI (SIH260011).

Public functions (this is the contract the backend team imports and calls):
    transcribe_audio(file_path) -> str
    normalize_text(text) -> {"canonical_text": str, "language": str}
    describe_image(file_path) -> str
    classify_complaint(text, image_description=None) -> dict
    classify_from_raw_input(text, image_description=None) -> dict
        Preferred entry point for RAW (untranslated) complaint text: decides
        for itself whether normalize_text() is needed (native Indic script)
        or should be skipped (English/Hinglish), then classifies. Use this
        instead of calling normalize_text() + classify_complaint() by hand.
    split_departments(text, classification) -> dict
        Phase 3. See docs/SPLIT_DEPARTMENTS_DESIGN.md §1 for the locked
        output contract.
    embed_text(text) -> {"vector": [768 floats]}

Reliability rules (must hold for every function):
    - Availability beats accuracy. A citizen must always be able to lodge a
      complaint; a roughly-classified ticket is worth far more than a failed
      submission. Every degradation below is chosen on that basis.
    - Every external call has a timeout (REQUEST_TIMEOUT_SECONDS, applied on
      the client), then up to MAX_RETRIES retries with a short delay, then
      rolls to the next model in the chain, then to Groq, then falls back to a
      safe default in the SAME shape, with "fallback": True added so callers
      can tell it happened.
    - The whole model-chain walk is bounded by CHAIN_BUDGET_SECONDS, because a
      submission that eventually succeeds after several minutes has already
      failed the person making it.
    - classify_complaint() NEVER returns a category/priority outside the
      allowed lists in categories.py.
    - No function raises an unhandled exception to the caller — backend
      intake must always succeed even if the AI layer is having a bad day.
"""
import json
import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from google import genai
from google.genai import types

from . import config
from .categories import (
    CATEGORIES,
    PRIORITIES,
    DEFAULT_CATEGORY,
    DEFAULT_PRIORITY,
    MAX_DEPARTMENTS,
)
from .prompts import (
    NORMALIZE_PROMPT_TEMPLATE,
    IMAGE_DESCRIBE_PROMPT,
    build_classification_prompt,
    build_split_departments_prompt,
)

logger = logging.getLogger("ai_service")

_client: Optional[genai.Client] = None


def _get_client() -> Optional[genai.Client]:
    """Lazily creates the Gemini client. Returns None if no API key is set,
    so callers can fall back cleanly instead of crashing on import."""
    global _client
    if _client is None and config.GEMINI_API_KEY:
        _client = genai.Client(
            api_key=config.GEMINI_API_KEY,
            # Without this the SDK waits indefinitely, so one hung connection
            # blocks an intake forever — the exact "citizen can't lodge a
            # complaint" outcome the fallback chain exists to prevent.
            # HttpOptions.timeout is in milliseconds.
            http_options=types.HttpOptions(timeout=config.REQUEST_TIMEOUT_SECONDS * 1000),
        )
    return _client


def _with_retry(fn, *args, **kwargs):
    """Runs fn up to (1 + MAX_RETRIES) times with a short delay between
    attempts. Returns the result, or raises the last exception if every
    attempt failed — callers are expected to catch this and fall back."""
    last_error = None
    for attempt in range(config.MAX_RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 — intentionally broad, this is a reliability boundary
            last_error = exc
            logger.warning("ai_service call failed (attempt %d/%d): %s", attempt + 1, config.MAX_RETRIES + 1, exc)
            if attempt < config.MAX_RETRIES:
                time.sleep(config.RETRY_DELAY_SECONDS)
    raise last_error


# ---------------------------------------------------------------------------
# Gemini model fallback chain
# ---------------------------------------------------------------------------
#
# Every free-tier model has its own RPM and RPD budget (see config.py for the
# table). Rather than retrying one model until its window clears — which is
# what the old single-model + Groq path did, and which stalls the whole intake
# during a demo burst — we walk the chain: a quota error benches that model
# and the same request goes straight to the next one.
#
# Bench state is process-wide, so it's shared across concurrent requests. The
# backend runs sync endpoints in a threadpool, hence the lock.

_model_available_at: dict = {}       # model -> unix ts before which to skip it
_model_disabled: set = set()         # models this key can't reach at all
_chain_lock = threading.Lock()


def _next_daily_reset() -> float:
    """Unix timestamp of the next midnight Pacific, when Google's free-tier
    daily quotas roll over. Falls back to a fixed UTC-8 offset if the tz
    database isn't available (Windows without `tzdata` installed), which at
    worst benches a model an hour longer than needed during PDT."""
    try:
        from zoneinfo import ZoneInfo

        pacific = ZoneInfo("America/Los_Angeles")
    except Exception:  # noqa: BLE001 — missing tzdata, not worth failing over
        pacific = timezone(timedelta(hours=-8))

    now = datetime.now(pacific)
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return tomorrow.timestamp()


def _classify_error(exc: Exception) -> tuple:
    """Maps an exception to (kind, bench_until).

    kind is one of:
      "quota"     — rate/daily limit hit; bench this model, move on immediately.
                    Retrying in place would just burn the same exhausted window.
      "missing"   — model doesn't exist, isn't enabled for this key, or doesn't
                    support this input (e.g. audio on a text-only model).
                    Disable permanently; it will never start working mid-run.
      "transient" — 5xx/network/timeout. Worth retrying the SAME model before
                    moving on, since the next model is no likelier to succeed.
    """
    text = f"{type(exc).__name__}: {exc}".lower()

    if "resource_exhausted" in text or "429" in text or "rate limit" in text or "quota" in text:
        # Google labels the violated quota, e.g. GenerateRequestsPerDayPerProjectPerModel.
        if "perday" in text.replace("_", "").replace("-", ""):
            return "quota", _next_daily_reset()
        return "quota", time.time() + config.RPM_COOLDOWN_SECONDS

    if "not_found" in text or "404" in text or "is not found" in text or "not supported" in text:
        return "missing", None

    return "transient", None


def _available_models() -> list:
    """The chain, minus models that are benched or disabled, in priority order."""
    now = time.time()
    with _chain_lock:
        return [
            m for m in config.GEMINI_TEXT_MODELS
            if m not in _model_disabled and _model_available_at.get(m, 0) <= now
        ]


def _bench(model: str, kind: str, until) -> None:
    with _chain_lock:
        if kind == "missing":
            _model_disabled.add(model)
        elif until is not None:
            _model_available_at[model] = until


def _generate_with_fallback(client: genai.Client, *, contents, gen_config=None, purpose: str):
    """Runs generate_content against the model chain and returns
    (response, model_name).

    Transient failures retry the same model up to MAX_RETRIES; quota failures
    bench it and move on with no retry. The whole walk is capped at
    CHAIN_BUDGET_SECONDS — see the note there on why finishing late is its own
    kind of failure. Raises the last exception when the chain is exhausted or
    the budget runs out; callers treat that as "the Gemini path is down" and
    fall through to their own safe default, which still lodges the complaint."""
    models = _available_models()
    if not models:
        # Everything is benched. Rather than give up, retry whichever model
        # frees up soonest — a stale bench shouldn't hard-fail an intake.
        with _chain_lock:
            candidates = [m for m in config.GEMINI_TEXT_MODELS if m not in _model_disabled]
        if not candidates:
            raise RuntimeError("every Gemini model in the chain is disabled for this API key")
        models = [min(candidates, key=lambda m: _model_available_at.get(m, 0))]
        logger.warning("%s: all models benched, forcing a retry on %s", purpose, models[0])

    deadline = time.time() + config.CHAIN_BUDGET_SECONDS
    last_error = None
    for model in models:
        if time.time() >= deadline:
            logger.warning(
                "%s: chain budget of %ss spent, giving up with %d model(s) untried",
                purpose, config.CHAIN_BUDGET_SECONDS, len(models) - models.index(model),
            )
            break
        for attempt in range(config.MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(
                    model=model, contents=contents, config=gen_config,
                )
                if model != config.GEMINI_TEXT_MODELS[0]:
                    logger.info("%s: answered by fallback model %s", purpose, model)
                return response, model
            except Exception as exc:  # noqa: BLE001 — reliability boundary
                last_error = exc
                kind, until = _classify_error(exc)

                if (
                    kind == "transient"
                    and attempt < config.MAX_RETRIES
                    and time.time() + config.RETRY_DELAY_SECONDS < deadline
                ):
                    logger.warning(
                        "%s: %s transient failure (attempt %d/%d): %s",
                        purpose, model, attempt + 1, config.MAX_RETRIES + 1, exc,
                    )
                    time.sleep(config.RETRY_DELAY_SECONDS)
                    continue

                _bench(model, kind, until)
                logger.warning("%s: %s failed (%s), falling through: %s", purpose, model, kind, exc)
                break  # next model in the chain

    raise last_error


def _extract_json(raw_text: str) -> dict:
    """Gemini is asked for raw JSON, but strips/handles the common case of
    it wrapping the answer in ```json ... ``` fences anyway."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ---------------------------------------------------------------------------
# transcribe_audio
# ---------------------------------------------------------------------------

def transcribe_audio(file_path: str) -> str:
    """Converts a voice-note audio file to text. Walks the Gemini model chain
    first (Gemini accepts audio directly); falls back to Groq's free Whisper
    endpoint if GROQ_API_KEY is set and every Gemini model fails; falls back
    to an empty string (never raises) if everything fails, so the caller can
    still create a ticket flagged for human review instead of losing the
    complaint. Groq matters more here than elsewhere — Whisper is a purpose-
    built transcription model, so it's a genuine upgrade over the last rungs
    of the Gemini chain rather than just a spare."""
    client = _get_client()
    if client is not None:
        try:
            return _transcribe_with_gemini(client, file_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini transcription chain failed, trying fallback: %s", exc)

    if config.GROQ_API_KEY:
        try:
            return _with_retry(_transcribe_with_groq, file_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("Groq transcription fallback also failed: %s", exc)

    logger.error("transcribe_audio: no working transcription path, returning empty string")
    return ""


def _transcribe_with_gemini(client: genai.Client, file_path: str) -> str:
    uploaded = _with_retry(client.files.upload, file=file_path)
    response, _model = _generate_with_fallback(
        client,
        contents=[
            uploaded,
            "Transcribe this audio exactly as spoken. If it is not in English, "
            "transcribe it in its original language/script — do not translate here.",
        ],
        purpose="transcribe_audio",
    )
    return (response.text or "").strip()


def _transcribe_with_groq(file_path: str) -> str:
    from groq import Groq  # imported lazily so this dependency is optional

    client = Groq(api_key=config.GROQ_API_KEY)
    with open(file_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
        )
    return (result.text or "").strip()


# ---------------------------------------------------------------------------
# normalize_text
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> dict:
    """Detects the language and translates/normalizes to clear English.
    Fallback: returns the original text unchanged with language 'unknown'
    and fallback=True, so downstream classification still runs on
    *something* rather than blocking."""
    client = _get_client()
    fallback = {"canonical_text": text, "language": "unknown", "fallback": True}
    if client is None:
        return fallback

    try:
        prompt = NORMALIZE_PROMPT_TEMPLATE.format(raw_text=text)
        response, _model = _generate_with_fallback(
            client,
            contents=prompt,
            gen_config=types.GenerateContentConfig(response_mime_type="application/json"),
            purpose="normalize_text",
        )
        parsed = _extract_json(response.text)
        return {
            "canonical_text": parsed.get("canonical_text") or text,
            "language": parsed.get("language") or "unknown",
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("normalize_text failed, returning original text: %s", exc)
        return fallback


# ---------------------------------------------------------------------------
# describe_image
# ---------------------------------------------------------------------------

def describe_image(file_path: str) -> str:
    """One-paragraph factual description of a complaint photo. Returns an
    empty string on failure (never raises) — classify_complaint() treats a
    missing image description as 'no photo context', not an error."""
    client = _get_client()
    if client is None:
        return ""

    try:
        return _describe_image_with_gemini(client, file_path)
    except Exception as exc:  # noqa: BLE001
        logger.error("describe_image failed, continuing without image context: %s", exc)
        return ""


def _describe_image_with_gemini(client: genai.Client, file_path: str) -> str:
    # The upload is done once, outside the chain — the uploaded file handle is
    # not model-specific, so re-uploading per fallback attempt would waste a
    # round trip. Any model in the chain that can't take image input reports
    # "not supported", which _classify_error benches permanently.
    uploaded = _with_retry(client.files.upload, file=file_path)
    response, _model = _generate_with_fallback(
        client,
        contents=[uploaded, IMAGE_DESCRIBE_PROMPT],
        purpose="describe_image",
    )
    return (response.text or "").strip()


# ---------------------------------------------------------------------------
# script detection (for classify_from_raw_input)
# ---------------------------------------------------------------------------

# Unicode blocks for the native scripts normalize_text() should run on. These
# ranges are contiguous (Devanagari through Malayalam sit back-to-back from
# U+0900), so this table also acts as one effective "native Indic script"
# range for the yes/no question.
_INDIC_SCRIPT_RANGES = [
    ("devanagari", 0x0900, 0x097F),  # Hindi, Marathi, etc.
    ("bengali", 0x0980, 0x09FF),
    ("gurmukhi", 0x0A00, 0x0A7F),  # Punjabi
    ("gujarati", 0x0A80, 0x0AFF),
    ("odia", 0x0B00, 0x0B7F),
    ("tamil", 0x0B80, 0x0BFF),
    ("telugu", 0x0C00, 0x0C7F),
    ("kannada", 0x0C80, 0x0CFF),
    ("malayalam", 0x0D00, 0x0D7F),
]


def _detect_native_script(text: str) -> Optional[str]:
    """Pure local check, no API call. Scans left to right and returns on the
    FIRST native-script character found — a single native character anywhere
    in the text (e.g. one Devanagari word dropped into an otherwise-English
    sentence) is enough to report that script, and classify_from_raw_input()
    will send the WHOLE string to normalize_text() on that basis. That's the
    intended behavior for code-mixed input: we don't try to split the string
    script-by-script, we just ask "does this need translation at all?"

    Returns None only when no character in `text` falls in a native-script
    range — i.e. the text is Latin-script only (English or Hinglish). That's
    also the worst case for runtime: every character gets checked against all
    9 ranges, which is fine at complaint length."""
    for ch in text:
        codepoint = ord(ch)
        for name, start, end in _INDIC_SCRIPT_RANGES:
            if start <= codepoint <= end:
                return name
    return None


# ---------------------------------------------------------------------------
# classify_complaint
# ---------------------------------------------------------------------------

def _fallback_classification() -> dict:
    return {
        "category": DEFAULT_CATEGORY,
        "subcategory": "unclassified",
        "priority": DEFAULT_PRIORITY,
        "confidence": 0.0,
        "location_text": None,
        "summary": "Could not be automatically classified — needs manual review.",
        "fallback": True,
        "source": "fallback",
    }


def classify_complaint(text: str, image_description: Optional[str] = None) -> dict:
    """The core function. Takes canonical (already-translated) complaint
    text and an optional image description, returns structured
    classification. ALWAYS validates category/priority against the allowed
    lists before returning — never passes through a value the model
    invented outside those lists.

    Provider chain: the Gemini model chain (config.GEMINI_TEXT_MODELS, in
    order) -> Groq (if GROQ_API_KEY is set) -> safe default. Each Gemini
    model has its own free-tier quota, so when one is rate-limited the same
    complaint rolls to the next model rather than dropping to confidence=0 —
    which is what used to happen during demos when several complaints came in
    close together. Groq stays on the end as an independent provider, for the
    case where Gemini is down as a whole rather than merely throttled; it gets
    the identical prompt, just run through a different model."""
    client = _get_client()
    if client is not None:
        try:
            prompt = build_classification_prompt(text, image_description)
            response, model = _generate_with_fallback(
                client,
                contents=prompt,
                gen_config=types.GenerateContentConfig(response_mime_type="application/json"),
                purpose="classify_complaint",
            )
            parsed = _extract_json(response.text)
            return _validate_classification(parsed, source="gemini", model=model)
        except Exception as exc:  # noqa: BLE001
            logger.error("classify_complaint: whole Gemini chain failed, trying Groq fallback: %s", exc)

    if config.GROQ_API_KEY:
        try:
            prompt = build_classification_prompt(text, image_description)
            parsed = _with_retry(_classify_with_groq, prompt)
            return _validate_classification(parsed, source="groq", model=config.GROQ_TEXT_MODEL)
        except Exception as exc:  # noqa: BLE001
            logger.error("classify_complaint: Groq fallback also failed, returning safe default: %s", exc)
    else:
        logger.warning("classify_complaint: Gemini chain failed and no GROQ_API_KEY is set, returning safe default")

    return _fallback_classification()


def _classify_with_groq(prompt: str) -> dict:
    """Sends the same classification prompt to Groq's free Llama endpoint.
    Raises on failure so _with_retry can retry/propagate — the caller
    catches and moves to the final safe-default fallback."""
    from groq import Groq  # imported lazily so this dependency is optional

    client = Groq(api_key=config.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=config.GROQ_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw_text = response.choices[0].message.content
    return _extract_json(raw_text)


def _validate_classification(parsed: dict, source: str, model: Optional[str] = None) -> dict:
    """Guards against the model returning a category/priority outside our
    fixed lists, a confidence outside [0, 1], or missing fields.

    `source` records which provider actually produced this answer
    ("gemini" or "groq") so callers/logs can tell them apart — useful for
    debugging and for knowing how often the Groq fallback is kicking in.
    `model` narrows that to the exact model, since "gemini" now covers a
    whole fallback chain and the rungs differ in accuracy; run_holdout.py
    keys its scoring off `source`, so that stays coarse deliberately."""
    category = parsed.get("category")
    if category not in CATEGORIES:
        logger.warning("classify_complaint: invalid category '%s', defaulting to '%s'", category, DEFAULT_CATEGORY)
        category = DEFAULT_CATEGORY

    priority = parsed.get("priority")
    if priority not in PRIORITIES:
        logger.warning("classify_complaint: invalid priority '%s', defaulting to '%s'", priority, DEFAULT_PRIORITY)
        priority = DEFAULT_PRIORITY

    try:
        confidence = float(parsed.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    # If we had to override the model's category/priority choice, the
    # confidence it reported no longer means anything — zero it out so the
    # backend correctly routes this to human review.
    if category != parsed.get("category") or priority != parsed.get("priority"):
        confidence = 0.0

    return {
        "category": category,
        "subcategory": parsed.get("subcategory") or "unspecified",
        "priority": priority,
        "confidence": confidence,
        "location_text": parsed.get("location_text") or None,
        "summary": parsed.get("summary") or "No summary available.",
        "source": source,
        "model": model,
    }


# ---------------------------------------------------------------------------
# classify_from_raw_input
# ---------------------------------------------------------------------------

def classify_from_raw_input(text: str, image_description: Optional[str] = None) -> dict:
    """The actual production entry point: takes RAW complaint text and decides
    for itself whether translation is needed. Runs normalize_text() first only
    when `text` contains native Indic script (Devanagari/Bengali/Gurmukhi/
    Gujarati/Odia/Tamil/Telugu/Kannada/Malayalam, via _detect_native_script());
    Latin-script text (English or Hinglish) goes straight to
    classify_complaint(), skipping translation entirely.

    Why conditional: holdout evidence (tests/holdout_results/holdout_normalized.json)
    shows translation is net-negative on Latin-script input specifically. Of
    the 2 failures in the --normalize run (vs 0 on raw text), only case 10
    (Hinglish) was a translation problem — normalize_text() dropped "dirty
    water entering the shops, no customers coming", which lost the detail
    that pushed priority from high down to medium. Case 26 (Devanagari)
    translated faithfully ("Street sweepers do not come on time and only do
    a formality") and the model still miscategorised it as garbage instead of
    sanitation — a classifier boundary problem, not a translation problem.
    Conditional normalization fixes the first failure mode but not the
    second, since case 26 is native script and will still be translated
    here. Expect this path to score ~29/30 on the current holdout, not 30/30.

    Returns the same dict shape as classify_complaint(), plus:
        normalized (bool):          whether normalize_text() actually ran AND
                                     succeeded (False if skipped as
                                     Latin-script, and also False if it ran
                                     but fell back internally)
        detected_script (str|None): which native script triggered translation,
                                     if any

    Never raises. If normalize_text() falls back internally (its own
    fallback=True), this falls back right along with it and classifies the
    original raw text rather than giving up.
    """
    detected_script = _detect_native_script(text)
    canonical_text = text
    normalized = False

    if detected_script is not None:
        result = normalize_text(text)
        if result.get("fallback"):
            logger.warning(
                "classify_from_raw_input: normalize_text fell back for detected "
                "script '%s', classifying raw text instead", detected_script,
            )
        else:
            canonical_text = result.get("canonical_text") or text
            normalized = True

    classification = classify_complaint(canonical_text, image_description)
    classification["normalized"] = normalized
    classification["detected_script"] = detected_script
    return classification


# ---------------------------------------------------------------------------
# split_departments (Phase 3)
# ---------------------------------------------------------------------------
# Locked output contract: docs/SPLIT_DEPARTMENTS_DESIGN.md §1. Do not change
# the shape below without updating that doc and the Team Integration Guide
# the same day.

_PRIORITY_SEVERITY = {"critical": 3, "high": 2, "medium": 1, "low": 0}


def _split_fallback(text: str, classification: dict) -> dict:
    """Design doc §1 rule 6: a failed split is NOT a failed classification,
    so confidence is carried through unchanged, not zeroed."""
    return {
        "is_split": False,
        "departments": [{
            "category": classification.get("category", DEFAULT_CATEGORY),
            "subcategory": classification.get("subcategory") or "unspecified",
            "priority": classification.get("priority", DEFAULT_PRIORITY),
            "confidence": classification.get("confidence", 0.0),
            "excerpt": text,
            "location_text": classification.get("location_text"),
        }],
        "source": "fallback",
        "fallback": True,
    }


def split_departments(text: str, classification: dict) -> dict:
    """Decides whether `classification` (already produced by
    classify_complaint() for this same `text`) should be broken into
    multiple department-routed pieces. See
    docs/SPLIT_DEPARTMENTS_DESIGN.md §1 for the full contract.

    Provider chain (Gemini model chain -> Groq -> safe default) and retry
    behavior mirror classify_complaint() exactly. The one difference is the
    fallback shape itself — see _split_fallback()."""
    client = _get_client()
    if client is not None:
        try:
            prompt = build_split_departments_prompt(text, classification)
            response, model = _generate_with_fallback(
                client,
                contents=prompt,
                gen_config=types.GenerateContentConfig(response_mime_type="application/json"),
                purpose="split_departments",
            )
            parsed = _extract_json(response.text)
            return _validate_split_departments(parsed, text, source="gemini", model=model)
        except Exception as exc:  # noqa: BLE001
            logger.error("split_departments: whole Gemini chain failed, trying Groq fallback: %s", exc)

    if config.GROQ_API_KEY:
        try:
            prompt = build_split_departments_prompt(text, classification)
            parsed = _with_retry(_split_departments_with_groq, prompt)
            return _validate_split_departments(parsed, text, source="groq", model=config.GROQ_TEXT_MODEL)
        except Exception as exc:  # noqa: BLE001
            logger.error("split_departments: Groq fallback also failed, returning single-department fallback: %s", exc)
    else:
        logger.warning("split_departments: Gemini chain failed and no GROQ_API_KEY is set, returning single-department fallback")

    return _split_fallback(text, classification)


def _split_departments_with_groq(prompt: str) -> dict:
    from groq import Groq  # imported lazily so this dependency is optional

    client = Groq(api_key=config.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=config.GROQ_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw_text = response.choices[0].message.content
    return _extract_json(raw_text)


def _validate_split_departments(parsed: dict, text: str, source: str, model: Optional[str] = None) -> dict:
    """Validates each department item by delegating to _validate_classification()
    (same category/priority/confidence rules as a single classification —
    reusing it instead of re-implementing keeps the two from silently
    drifting apart), then adds the split-specific `excerpt` field. Enforces
    the design doc's max-4 cap (rule 3) by keeping the highest
    severity/confidence items, and always leaves at least one department —
    including when every raw item is unusable — so the "departments is
    always a non-empty list" contract (design doc §1 rule 1) can't be
    violated. Derives `is_split` from the final department count rather
    than trusting a model-reported flag, so the two can never disagree."""
    raw_departments = parsed.get("departments")
    if not isinstance(raw_departments, list) or not raw_departments:
        logger.warning("split_departments: response had no usable 'departments' list, treating as single unclassified department")
        raw_departments = [{}]

    departments = []
    for item in raw_departments:
        if not isinstance(item, dict):
            continue
        validated = _validate_classification(item, source, model)
        departments.append({
            "category": validated["category"],
            "subcategory": validated["subcategory"],
            "priority": validated["priority"],
            "confidence": validated["confidence"],
            "excerpt": item.get("excerpt") or text,
            "location_text": validated["location_text"],
        })

    if not departments:
        logger.warning("split_departments: every department item was unusable, treating as single unclassified department")
        departments.append({
            "category": DEFAULT_CATEGORY,
            "subcategory": "unspecified",
            "priority": DEFAULT_PRIORITY,
            "confidence": 0.0,
            "excerpt": text,
            "location_text": None,
        })

    if len(departments) > MAX_DEPARTMENTS:
        departments.sort(key=lambda d: (_PRIORITY_SEVERITY[d["priority"]], d["confidence"]), reverse=True)
        departments = departments[:MAX_DEPARTMENTS]

    return {
        "is_split": len(departments) > 1,
        "departments": departments,
        "source": source,
        "model": model,
        "fallback": False,
    }


# ---------------------------------------------------------------------------
# embed_text
# ---------------------------------------------------------------------------

def embed_text(text: str) -> dict:
    """Returns a 768-dimension embedding vector for the given text, matching
    the backend's pgvector column size (see Team Integration Guide's Locked
    Decisions). Fallback: a zero-vector with fallback=True — this is
    intentionally a "neutral" vector that won't falsely match as a
    duplicate of anything, rather than a random one."""
    client = _get_client()
    fallback_vector = [0.0] * config.EMBEDDING_DIMENSIONS

    if client is None:
        return {"vector": fallback_vector, "fallback": True}

    try:
        response = _with_retry(
            client.models.embed_content,
            model=config.GEMINI_EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=config.EMBEDDING_DIMENSIONS),
        )
        vector = list(response.embeddings[0].values)
        if len(vector) != config.EMBEDDING_DIMENSIONS:
            logger.warning(
                "embed_text: unexpected vector size %d (expected %d), using fallback",
                len(vector), config.EMBEDDING_DIMENSIONS,
            )
            return {"vector": fallback_vector, "fallback": True}
        return {"vector": vector}
    except Exception as exc:  # noqa: BLE001
        logger.error("embed_text failed, returning fallback zero-vector: %s", exc)
        return {"vector": fallback_vector, "fallback": True}