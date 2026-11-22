"""
Run this after any prompt/example change to eyeball accuracy:

    python -m ai_service.tests.run_examples

Runs classify_complaint() on all 15 few-shot examples (to sanity-check the
model actually follows its own examples) PLUS 5 edge cases designed to
expose weaknesses. Prints a results table — no assertions, this is a
by-eye accuracy check, not a pass/fail test suite.
"""
import time

from ai_service.examples import FEW_SHOT_EXAMPLES
from ai_service.service import classify_complaint

# Free-tier Gemini keys have a low requests-per-minute quota (5-15
# depending on model). This script fires 20 calls in a row, so we pace
# them out to avoid tripping 429 RESOURCE_EXHAUSTED errors and falling
# back near the end of the run. 15s keeps us comfortably under a 15
# RPM quota even accounting for retries. If you still see 429s, raise this.
SECONDS_BETWEEN_CALLS = 15

EDGE_CASES = [
    "",  # empty text
    "bad",  # one word, essentially meaningless
    "ನೀರಿನ ಸಮಸ್ಯೆ ಇದೆ ನಮ್ಮ ಏರಿಯಾದಲ್ಲಿ",  # pure Kannada — no English/Hindi at all
    "This is absolutely the WORST city ever, nothing works, I'm so angry, someone needs to fix this whole area right now!!!",  # angry rant, no clear specific issue
    "Ek pipeline leak ho rahi thi jiski wajah se sadak ka ek bada hissa dhas gaya hai aur traffic bhi ruk gaya hai",  # spans two departments (water + roads)
]


def _truncate(text: str, length: int = 55) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= length else text[: length - 3] + "..."


def main():
    rows = []

    print(f"\nRunning {len(FEW_SHOT_EXAMPLES)} few-shot examples "
          f"(pacing {SECONDS_BETWEEN_CALLS}s between calls to respect free-tier rate limits)...\n")
    for i, ex in enumerate(FEW_SHOT_EXAMPLES):
        if i > 0:
            time.sleep(SECONDS_BETWEEN_CALLS)
        result = classify_complaint(ex["text"])
        expected = ex["output"]
        match = "✓" if result["category"] == expected["category"] and result["priority"] == expected["priority"] else "✗"
        rows.append((match, _truncate(ex["text"]), result["category"], result["priority"], round(result["confidence"], 2), result.get("source", "?")))

    print(f"\nRunning {len(EDGE_CASES)} edge cases (no expected answer — eyeball these)...\n")
    for text in EDGE_CASES:
        time.sleep(SECONDS_BETWEEN_CALLS)
        result = classify_complaint(text)
        rows.append(("?", _truncate(text or "(empty string)"), result["category"], result["priority"], round(result["confidence"], 2), result.get("source", "?")))

    header = f"{'':2} {'Input':<57} {'Category':<15} {'Priority':<10} {'Conf':<5} {'Source':<8}"
    print(header)
    print("-" * len(header))
    for match, text, category, priority, confidence, source in rows:
        print(f"{match:<2} {text:<57} {category:<15} {priority:<10} {confidence:<5} {source:<8}")

    mismatches = sum(1 for r in rows if r[0] == "✗")
    print(f"\n{mismatches} mismatch(es) out of {len(FEW_SHOT_EXAMPLES)} few-shot examples "
          f"(edge cases have no fixed expected answer — review manually).")


if __name__ == "__main__":
    main()