"""
Scores classify_complaint() against the HELD-OUT test set.

    python -m ai_service.tests.run_holdout

This is the real accuracy number. run_examples.py grades the model on the same
15 examples that are baked into its own prompt — open book, which is why it
scores 15/15. This scores it on 30 complaints it has never seen.

Options:
    --normalize        Always run normalize_text() first, then classify.
                        Doubles the API calls and therefore the runtime.
                        See "WHICH PATH AM I TESTING?" below.
    --smart-normalize   Run classify_from_raw_input(): normalize_text() only
                        runs when native Indic script is detected, Latin-script
                        text (English/Hinglish) classifies directly. This is
                        the actual current production entry point.
    --start N       Skip the first N cases (for resuming a chunked run)
    --limit N       Only run N cases
    --delay N       Seconds between API calls (default 15, for free-tier limits)
    --batch N       TEST-ONLY: classify N cases per API call instead of one
                     per call (see ai_service/tests/batch_classify.py). Cuts
                     request count by ~Nx — use this when a provider's
                     per-day or per-minute request-count limit, not raw
                     throughput, is what's blocking a full run. Forces raw
                     mode (no translation, incompatible with --normalize /
                     --smart-normalize) and always tries Gemini then falls
                     back to Groq for the whole batch, mirroring the
                     production provider chain at the batch level.

WHICH PATH AM I TESTING?
    By default this calls classify_complaint(raw_text) directly, which is what
    run_examples.py does. --normalize always translates first — for the
    Kannada/Tamil/Telugu/Hindi cases in the holdout set that's a meaningfully
    different test. --smart-normalize translates conditionally, matching what
    classify_from_raw_input() actually does in production. Run all three and
    compare: if --normalize scores worse than raw, translation is losing
    detail somewhere; --smart-normalize shows whether skipping translation for
    already-Latin text recovers that loss.

READING THE OUTPUT:
    The headline number is EXACT MATCH (category AND priority both right).
    But the number that actually matters for the product is in the CONFIDENCE
    CALIBRATION section: this system routes anything below the human-review
    threshold to a person. So a wrong answer with low confidence is a caught
    error, not a failure. A wrong answer with HIGH confidence is the dangerous
    kind — that's a misrouted ticket nobody double-checks.
"""
import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict

# The holdout set is 3/4 non-English and the report prints complaint text in
# its original script. On a Windows console defaulting to cp1252 that is an
# immediate UnicodeEncodeError — and because report() runs BEFORE the results
# file is written, that crash used to destroy a completed 200-case run's
# output. Force UTF-8 and degrade unencodable characters instead.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai_service.categories import HUMAN_REVIEW_CONFIDENCE_THRESHOLD
from ai_service.service import (
    _detect_native_script,
    classify_complaint,
    classify_from_raw_input,
    normalize_text,
)
from ai_service.tests import batch_classify
from ai_service.tests.holdout_set import HOLDOUT_SET

MODE_LABELS = {
    "raw": "classify on raw text",
    "normalize": "normalize -> classify (always translate)",
    "smart": "classify_from_raw_input (smart: translate only if native script)",
}

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "holdout_results")


def _accepted_categories(case: dict) -> list:
    return [case["expected_category"]] + list(case.get("also_accept_category", []))


def _accepted_priorities(case: dict) -> list:
    return [case["expected_priority"]] + list(case.get("also_accept_priority", []))


def _truncate(text: str, length: int = 60) -> str:
    text = " ".join(text.split())
    return text if len(text) <= length else text[: length - 1] + "…"


def _mark_for(row: dict) -> str:
    if row.get("source") == "error":
        return "!"
    if row.get("source") == "fallback":
        return "-"
    if row["exact_ok"]:
        return "OK"
    if row["category_ok"]:
        return "~"   # right department, wrong urgency
    return "X"


def _build_row(case: dict, result: dict, *, normalized_text=None, detected_language=None,
                detected_script=None, took_translation_path=None) -> dict:
    """Turns one classification result into the row shape report() expects.
    Shared by run_case() (one API call per case) and run_batch_chunk() (one
    API call per N cases) so both paths score identically regardless of how
    the answer was obtained."""
    got_category = result.get("category")
    got_priority = result.get("priority")
    category_ok = got_category in _accepted_categories(case)
    priority_ok = got_priority in _accepted_priorities(case)

    return {
        "text": case["text"],
        "normalized_text": normalized_text,
        "detected_language": detected_language,
        "detected_script": detected_script,
        "took_translation_path": took_translation_path,
        "expected_category": case["expected_category"],
        "expected_priority": case["expected_priority"],
        "got_category": got_category,
        "got_priority": got_priority,
        "category_ok": category_ok,
        "priority_ok": priority_ok,
        "exact_ok": category_ok and priority_ok,
        "confidence": result.get("confidence", 0.0),
        "source": result.get("source", "?"),
        "summary": result.get("summary"),
        "location_text": result.get("location_text"),
        "borderline": bool(case.get("borderline")),
        "note": case.get("note"),
        "lang": case.get("lang"),
        "tags": case.get("tags"),
    }


def run_case(case: dict, mode: str) -> dict:
    """Classifies one holdout case under the given mode and grades it. Never
    raises — a case that blows up is recorded as an error row rather than
    killing the whole run, because a 25-minute run dying on case 28 is
    miserable.

    mode:
        "raw"       -- classify_complaint(text) directly, no translation
        "normalize" -- normalize_text() then classify_complaint(), always
                       translates regardless of script
        "smart"     -- classify_from_raw_input(), translates only when
                       _detect_native_script() finds native Indic script
    """
    text = case["text"]
    language = None
    detected_script = None
    took_translation_path = None
    try:
        if mode == "normalize":
            normalized = normalize_text(text)
            text = normalized.get("canonical_text") or text
            language = normalized.get("language")
            result = classify_complaint(text)
        elif mode == "smart":
            result = classify_from_raw_input(text)
            detected_script = result.get("detected_script")
            took_translation_path = detected_script is not None
        else:
            result = classify_complaint(text)
    except Exception as exc:  # noqa: BLE001 — a scorer must never crash mid-run
        return {
            "text": case["text"],
            "error": f"{type(exc).__name__}: {exc}",
            "source": "error",
        }

    return _build_row(
        case, result,
        normalized_text=text if mode == "normalize" else None,
        detected_language=language,
        detected_script=detected_script,
        took_translation_path=took_translation_path,
    )


def run_batch_chunk(chunk: list) -> list:
    """TEST-ONLY: classifies a chunk of holdout cases in ONE API call via
    ai_service.tests.batch_classify, and returns row dicts in the same
    shape run_case() produces. Always raw mode (no translation) — see
    batch_classify's module docstring for why. Never raises."""
    texts = [c["text"] for c in chunk]
    try:
        results = batch_classify.classify_batch(texts)
    except Exception as exc:  # noqa: BLE001 — a scorer must never crash mid-run
        return [
            {"text": c["text"], "error": f"{type(exc).__name__}: {exc}", "source": "error"}
            for c in chunk
        ]
    return [_build_row(case, result) for case, result in zip(chunk, results)]


def report(rows: list, mode: str) -> dict:
    """Prints the scorecard and returns the summary dict that gets saved."""
    errors = [r for r in rows if r.get("source") == "error"]
    fallbacks = [r for r in rows if r.get("source") == "fallback"]

    # Rows the AI layer never actually answered can't be scored as wrong —
    # they'd understate real accuracy. They're reported separately instead.
    scored = [r for r in rows if r.get("source") in ("gemini", "groq")]

    print("\n" + "=" * 78)
    print(f"HOLDOUT SCORECARD  ({MODE_LABELS[mode]})")
    print("=" * 78)

    if not scored:
        print("\nNothing was scored — every call fell back or errored.")
        print("Check your API key and rate limits, then re-run.")
        return {"scored": 0, "errors": len(errors), "fallbacks": len(fallbacks), "mode": mode}

    n = len(scored)
    cat_hits = sum(1 for r in scored if r["category_ok"])
    pri_hits = sum(1 for r in scored if r["priority_ok"])
    exact_hits = sum(1 for r in scored if r["exact_ok"])

    print(f"\nScored {n} of {len(rows)} cases"
          f"   (excluded: {len(fallbacks)} fallback, {len(errors)} error)")
    print(f"\n  Category correct    {cat_hits:>3}/{n}   {cat_hits / n:6.1%}")
    print(f"  Priority correct    {pri_hits:>3}/{n}   {pri_hits / n:6.1%}")
    print(f"  EXACT MATCH         {exact_hits:>3}/{n}   {exact_hits / n:6.1%}   <-- headline")

    # Strict score: borderline cases counted against their primary label only.
    strict = [r for r in scored if not r["borderline"]]
    if strict:
        strict_exact = sum(1 for r in strict if r["exact_ok"])
        print(f"\n  Excluding the {len(scored) - len(strict)} borderline cases:"
              f"   {strict_exact}/{len(strict)}   {strict_exact / len(strict):6.1%}")

    # ---- per-language breakdown ------------------------------------------
    print("\n" + "-" * 78)
    print("BY LANGUAGE")
    print("-" * 78)
    langs = sorted({r.get("lang") for r in scored}, key=lambda x: (x is None, x or ""))
    print(f"  {'lang':<10} {'n':>4}   {'category':>10}   {'priority':>10}   {'exact':>10}")
    for lang in langs:
        rows_l = [r for r in scored if r.get("lang") == lang]
        nl = len(rows_l)
        cat_l = sum(1 for r in rows_l if r["category_ok"]) / nl
        pri_l = sum(1 for r in rows_l if r["priority_ok"]) / nl
        exact_l = sum(1 for r in rows_l if r["exact_ok"]) / nl
        label = lang if lang else "?"
        print(f"  {label:<10} {nl:>4}   {cat_l:>9.1%}   {pri_l:>9.1%}   {exact_l:>9.1%}")

    translated_count = direct_count = None
    if mode == "smart":
        translated = [r for r in scored if r.get("took_translation_path")]
        direct = [r for r in scored if not r.get("took_translation_path")]
        translated_count, direct_count = len(translated), len(direct)
        print("\n" + "-" * 78)
        print("TRANSLATION PATH SPLIT")
        print("-" * 78)
        print(f"  translated (native script detected)   {translated_count:>3}/{n}")
        print(f"  direct (Latin script, skipped)         {direct_count:>3}/{n}")
        scripts = Counter(r["detected_script"] for r in translated)
        if scripts:
            print("  scripts seen: " + ", ".join(f"{name} x{count}" for name, count in scripts.most_common()))

        print(f"\n  {'path':<10} {'n':>4}   {'category':>10}   {'priority':>10}   {'exact':>10}")
        for path_name, rows_p in (("translated", translated), ("direct", direct)):
            if not rows_p:
                continue
            npth = len(rows_p)
            cat_p = sum(1 for r in rows_p if r["category_ok"]) / npth
            pri_p = sum(1 for r in rows_p if r["priority_ok"]) / npth
            exact_p = sum(1 for r in rows_p if r["exact_ok"]) / npth
            print(f"  {path_name:<10} {npth:>4}   {cat_p:>9.1%}   {pri_p:>9.1%}   {exact_p:>9.1%}")

    # ---- where it went wrong -------------------------------------------
    cat_misses = [r for r in scored if not r["category_ok"]]
    if cat_misses:
        print("\n" + "-" * 78)
        print("CATEGORY MISSES")
        print("-" * 78)
        pairs = Counter((r["expected_category"], r["got_category"]) for r in cat_misses)
        for (want, got), count in pairs.most_common():
            print(f"  {want:>14}  ->  {got:<14}  x{count}")

    pri_misses = [r for r in scored if not r["priority_ok"]]
    if pri_misses:
        print("\n" + "-" * 78)
        print("PRIORITY MISSES")
        print("-" * 78)
        pairs = Counter((r["expected_priority"], r["got_priority"]) for r in pri_misses)
        for (want, got), count in pairs.most_common():
            direction = "OVER-escalated" if _severity(got) > _severity(want) else "UNDER-escalated"
            print(f"  {want:>10}  ->  {got:<10}  x{count}   ({direction})")

        over = sum(1 for r in pri_misses if _severity(r["got_priority"]) > _severity(r["expected_priority"]))
        under = len(pri_misses) - over
        print(f"\n  {over} over-escalated (wastes officer time), "
              f"{under} under-escalated (real risk — a critical treated as routine)")

    # ---- confidence calibration ----------------------------------------
    print("\n" + "-" * 78)
    print(f"CONFIDENCE CALIBRATION  (human-review threshold = {HUMAN_REVIEW_CONFIDENCE_THRESHOLD})")
    print("-" * 78)

    right = [r for r in scored if r["exact_ok"]]
    wrong = [r for r in scored if not r["exact_ok"]]
    if right:
        print(f"  mean confidence when CORRECT    {sum(r['confidence'] for r in right) / len(right):.2f}")
    if wrong:
        print(f"  mean confidence when WRONG      {sum(r['confidence'] for r in wrong) / len(wrong):.2f}")
        print("  (want a clear gap here — if they're close, confidence isn't")
        print("   telling you anything and the review threshold can't work)")

    caught = [r for r in wrong if r["confidence"] < HUMAN_REVIEW_CONFIDENCE_THRESHOLD]
    escaped = [r for r in wrong if r["confidence"] >= HUMAN_REVIEW_CONFIDENCE_THRESHOLD]
    flagged_ok = [r for r in right if r["confidence"] < HUMAN_REVIEW_CONFIDENCE_THRESHOLD]

    print(f"\n  Routing everything below {HUMAN_REVIEW_CONFIDENCE_THRESHOLD} to a human would:")
    print(f"    catch    {len(caught):>3} of {len(wrong)} wrong answers")
    print(f"    MISS     {len(escaped):>3} wrong answers that looked confident   <-- the dangerous ones")
    print(f"    cost     {len(flagged_ok):>3} needless reviews of correct answers")

    if escaped:
        print("\n  Confidently wrong:")
        for r in escaped:
            print(f"    [{r['confidence']:.2f}] {_truncate(r['text'], 52)}")
            print(f"           want {r['expected_category']}/{r['expected_priority']}"
                  f"  got {r['got_category']}/{r['got_priority']}")

    # ---- every miss, in full -------------------------------------------
    all_misses = [r for r in scored if not r["exact_ok"]]
    if all_misses:
        print("\n" + "-" * 78)
        print("ALL MISSES IN DETAIL")
        print("-" * 78)
        for r in all_misses:
            tag = " [borderline]" if r["borderline"] else ""
            print(f"\n  {_truncate(r['text'], 70)}{tag}")
            print(f"    want: {r['expected_category']}/{r['expected_priority']}"
                  f"    got: {r['got_category']}/{r['got_priority']}"
                  f"    conf {r['confidence']:.2f}  via {r['source']}")
            if r.get("normalized_text"):
                print(f"    normalized: {_truncate(r['normalized_text'], 66)}")
            if mode == "smart":
                path = f"translated (script: {r['detected_script']})" if r.get("took_translation_path") else "direct (Latin script, no translation)"
                print(f"    path: {path}")
            if r.get("note"):
                print(f"    label reason: {r['note']}")

    # ---- provider mix ---------------------------------------------------
    sources = Counter(r.get("source") for r in rows)
    print("\n" + "-" * 78)
    print("PROVIDER MIX")
    print("-" * 78)
    for source, count in sources.most_common():
        print(f"  {source:<10} {count}")
    if sources.get("groq"):
        print("\n  Note: some answers came from the Groq fallback, so this score")
        print("  is a blend of two models. Re-run when Gemini isn't throttled")
        print("  for a clean single-model number.")

    return {
        "scored": n,
        "total": len(rows),
        "fallbacks": len(fallbacks),
        "errors": len(errors),
        "category_accuracy": cat_hits / n,
        "priority_accuracy": pri_hits / n,
        "exact_accuracy": exact_hits / n,
        "mean_confidence_correct": (sum(r["confidence"] for r in right) / len(right)) if right else None,
        "mean_confidence_wrong": (sum(r["confidence"] for r in wrong) / len(wrong)) if wrong else None,
        "confidently_wrong": len(escaped),
        "provider_mix": dict(sources),
        "mode": mode,
        "used_normalize": mode == "normalize",
        "translated_count": translated_count,
        "direct_count": direct_count,
    }


_SEVERITY = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def _severity(priority: str) -> int:
    return _SEVERITY.get(priority, -1)


def main():
    parser = argparse.ArgumentParser(description="Score the classifier against the held-out set.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--normalize", action="store_true",
                        help="run normalize_text() first for every case (always translates)")
    mode_group.add_argument("--smart-normalize", action="store_true",
                        help="run classify_from_raw_input() (translates only when native script is detected)")
    parser.add_argument("--start", type=int, default=0, help="skip the first N cases")
    parser.add_argument("--limit", type=int, default=None, help="only run N cases")
    parser.add_argument("--delay", type=float, default=15.0,
                        help="seconds between calls (default 15 for free-tier limits)")
    parser.add_argument("--batch", type=int, default=None,
                        help="TEST-ONLY: classify N cases per API call instead of 1 "
                             "(cuts request count ~Nx; incompatible with --normalize/--smart-normalize)")
    args = parser.parse_args()

    if args.smart_normalize:
        mode = "smart"
    elif args.normalize:
        mode = "normalize"
    else:
        mode = "raw"

    if args.batch and mode != "raw":
        parser.error("--batch always runs raw (no translation) — drop --normalize/--smart-normalize to use it")
    if args.batch is not None and args.batch < 1:
        parser.error("--batch must be at least 1")

    cases = HOLDOUT_SET[args.start:]
    if args.limit:
        cases = cases[: args.limit]

    # In smart mode, only cases with native script make a second (translate)
    # API call — precompute which ones so the runtime estimate and the
    # inter-call delay both reflect the real number of calls, not a worst
    # case of "every case translates".
    will_translate = [_detect_native_script(c["text"]) is not None for c in cases] if mode == "smart" else None

    if args.batch:
        total_calls = -(-len(cases) // args.batch)  # ceil division
    elif mode == "normalize":
        total_calls = len(cases) * 2
    elif mode == "smart":
        total_calls = sum(2 if t else 1 for t in will_translate)
    else:
        total_calls = len(cases)
    est_minutes = (total_calls * args.delay) / 60
    batch_note = f", {args.batch} cases/call" if args.batch else ""
    print(f"\nRunning {len(cases)} holdout cases ({MODE_LABELS[mode]}{batch_note}),"
          f" {args.delay:g}s between calls ({total_calls} calls total).")
    print(f"Estimated runtime: ~{est_minutes:.0f} minutes. Progress prints as it goes.\n")

    rows = []
    os.makedirs(RESULTS_DIR, exist_ok=True)
    partial_path = os.path.join(RESULTS_DIR, "_partial.json")

    if args.batch:
        chunks = [cases[i:i + args.batch] for i in range(0, len(cases), args.batch)]
        done = 0
        for ci, chunk in enumerate(chunks):
            if ci > 0:
                time.sleep(args.delay)

            chunk_rows = run_batch_chunk(chunk)
            rows.extend(chunk_rows)
            done += len(chunk)

            with open(partial_path, "w", encoding="utf-8") as fh:
                json.dump(rows, fh, ensure_ascii=False, indent=2)

            print(f"  [batch {ci + 1}/{len(chunks)}] {len(chunk)} cases -> "
                  f"{' '.join(_mark_for(r) for r in chunk_rows)}   "
                  f"({args.start + done}/{args.start + len(cases)} done)")
    else:
        for i, case in enumerate(cases):
            if i > 0:
                time.sleep(args.delay)
            if i > 0 and (mode == "normalize" or (mode == "smart" and will_translate[i])):
                time.sleep(args.delay)  # this case makes a second API call, give it its own slot

            row = run_case(case, mode)
            rows.append(row)

            # Save after every case — a 25-minute run should never lose its work
            # to a crash or a Ctrl-C on case 29.
            with open(partial_path, "w", encoding="utf-8") as fh:
                json.dump(rows, fh, ensure_ascii=False, indent=2)

            print(f"  [{args.start + i + 1:>2}/{args.start + len(cases)}] {_mark_for(row):<2} "
                  f"{_truncate(case['text'], 56)}")

    suffix = {"raw": "raw", "normalize": "normalized", "smart": "smart"}[mode]
    if args.batch:
        suffix += f"_batch{args.batch}"
    out_path = os.path.join(RESULTS_DIR, f"holdout_{suffix}.json")

    # Write the rows BEFORE reporting. report() only formats what is already
    # decided, but it is also the one part of this script that can still
    # raise (it prints complaint text, sorts, divides) — and a crash there
    # after a full run would otherwise throw away every API call just spent.
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"summary": None, "rows": rows}, fh, ensure_ascii=False, indent=2)

    summary = report(rows, mode)

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, ensure_ascii=False, indent=2)
    if os.path.exists(partial_path):
        os.remove(partial_path)

    print(f"\nFull results saved to: {out_path}")
    print("Commit this file. After any prompt or example change, re-run and")
    print("diff the two — that's how you tell an improvement from a regression.\n")


if __name__ == "__main__":
    main()
