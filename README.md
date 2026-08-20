# ai_service — Phase 1

The AI/ML layer for GrievanceAI (SIH260011). This phase covers everything backend's Phase 1 (core intake + routing) needs from us.

## What's in Phase 1

- `transcribe_audio(file_path)` → text (Gemini, with a Groq Whisper fallback if `GROQ_API_KEY` is set)
- `normalize_text(text)` → `{"canonical_text", "language"}` — translates/cleans regional language or Hinglish input to clear English
- `describe_image(file_path)` → one-paragraph description of a complaint photo
- `classify_complaint(text, image_description=None)` → `{"category", "subcategory", "priority", "confidence", "location_text", "summary", "source"}` — `source` is `"gemini"`, `"groq"`, or `"fallback"`, telling you which provider actually answered
- `embed_text(text)` → `{"vector": [768 floats]}`

**Not in this phase:** `split_departments` (multi-department splitting) — that's Phase 3, built later once this is solid.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and paste in your free Gemini API key from https://aistudio.google.com/
```

## Testing your changes

There are two test scripts and they measure different things. **Both matter, and the second one is the honest one.**

### 1. Sanity check (open book)

```bash
python -m ai_service.tests.run_examples
```

Runs the 15 few-shot examples plus 5 adversarial edge cases. Note what this actually proves: it grades the model on the same examples that are baked into its own prompt. Scoring 15/15 means the prompt is well-formed and the model follows instructions — it does **not** mean the classifier is 90%+ accurate. Treat a drop here as a red flag, not a passing grade.

### 2. Real accuracy (closed book)

```bash
python -m ai_service.tests.run_holdout
```

Scores the classifier against 30 complaints in `tests/holdout_set.py` that it has never seen. This is the number to quote. Takes ~8 minutes because it paces calls to stay under the free-tier rate limit.

Useful flags:

- `--normalize` — run the real production path (`normalize_text` → `classify`) instead of classifying raw text. Doubles runtime. Worth running once to see whether the translation step helps or hurts on the regional-language cases.
- `--start N` / `--limit N` — run in chunks if you get rate-limited partway
- `--delay N` — seconds between calls (default 15)

Results save to `tests/holdout_results/`. **Commit that file.** After any prompt or example change, re-run and diff against the previous run — that's the only way to tell an improvement from a regression.

The section to read first is **CONFIDENCE CALIBRATION**. Accuracy alone isn't the product goal: anything below the review threshold goes to a human, so a wrong answer with low confidence is a caught error. The number that hurts is *confidently wrong* — a misrouted ticket nobody double-checks.

**Never copy anything from `holdout_set.py` into `examples.py`.** The moment a test complaint appears in the prompt it stops being a test and the score becomes meaningless.

## How this connects to the rest of the team

- **Backend** imports this package directly: `from ai_service import classify_complaint, embed_text, ...` and calls these functions inside the intake flow. The exact output shapes above are the contract — don't change a field name without updating the Team Integration Guide and telling backend the same day.
- **Prompt changes** happen in `prompts.py` only. If you're iterating wording with Gemini/ChatGPT (see the Team Integration Guide's prompts for that), paste the final version into `CLASSIFICATION_SYSTEM_INSTRUCTION` and re-run the test script.
- **Example changes** happen in `examples.py` only — replace the whole list when refining, not piecemeal edits, since the prompt is tuned against the set as a whole.

## Reliability behavior (already built in)

Every function times out, retries twice, then returns a safe fallback with `"fallback": true` in the response — never raises an exception. This means the backend can call these functions with confidence that intake will always succeed, even if:

- No API key is configured yet
- The free-tier rate limit is hit
- Gemini is temporarily down or slow
- The model returns a category/priority outside our allowed list (this gets caught and corrected, with confidence forced to 0 so it routes to human review)

**Two-provider fallback:** `classify_complaint()` and `transcribe_audio()` both try Gemini first, and if that fails (rate limit, outage, etc.) fall back to Groq's free tier as a second, independent provider before finally giving up to the safe default. This matters most during a live demo — Gemini's free tier can rate-limit at only 5-15 requests/minute depending on the model, and if several complaints land in the same minute, Groq catches the overflow instead of every subsequent complaint silently dropping to `confidence: 0`. Set `GROQ_API_KEY` in `.env` to enable this (it's optional — everything still works without it, just with one less safety net).

## What's next (Phase 2 / Phase 3, not built yet)

- Phase 2 (SLA + escalation) needs no new AI function — that's backend/scheduling logic.
- Phase 3 adds `split_departments(text, classification)` for multi-department complaints. Build this only once Phase 1 has been tested against real backend integration. Output contract is locked in `docs/SPLIT_DEPARTMENTS_DESIGN.md`.
