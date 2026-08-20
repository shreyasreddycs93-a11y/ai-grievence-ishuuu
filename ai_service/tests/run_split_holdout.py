"""
Scores split_departments() against the Phase 3 held-out set.

    python -m ai_service.tests.run_split_holdout

This is the Phase 3 counterpart to run_holdout.py. It is a SEPARATE scorer on
a SEPARATE set for a reason: run_holdout.py scores classify_complaint(), which
returns exactly one category by design and cannot split. Mixing the two sets
would break both -- holdout_set.py's 30 PAIR groups depend on staying intact,
and its cases carry expected_category/expected_priority where these carry
expected_departments (a list). Different function, different schema, different
file.

Options:
    --start N   Skip the first N cases (for resuming a chunked run)
    --limit N   Only run N cases
    --delay N   Seconds between API calls (default 15, for free-tier limits)
    --stub-classification
                Skip the classify_complaint() call and pass a neutral
                placeholder classification instead, HALVING the API calls
                (2 per case -> 1). Isolates splitting behavior from
                classification quality. NOT the production path: production
                always feeds split_departments() a real classification, so a
                score taken this way is a component test, not an end-to-end
                one. The placeholder is deliberately neutral (other/medium,
                confidence 0.0) so no ground truth leaks into the input.

HOW SCORING WORKS:
    Departments are compared as a MULTISET of (category, priority) tuples --
    order is not significant, since "roads then garbage" and "garbage then
    roads" are the same routing decision. A case passes exact match when the
    returned multiset equals expected_departments, or equals
    also_accept_departments on a borderline case.

READING THE OUTPUT:
    The headline is EXACT MATCH, but the number that decides whether this
    feature can ship is the OVER-SPLIT RATE. The design spec
    (docs/SPLIT_DEPARTMENTS_DESIGN.md Section 2) makes over-splitting the
    costlier failure on purpose: a false split dispatches two departments to
    one problem, while a missed split only leaves one department fixing
    something slightly outside its lane. A model that scores well overall but
    over-splits the trap cases (4-9) is not shippable.
"""
import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict

# This set is 7/25 native-script (Tamil, Kannada, Telugu, Bengali, Devanagari)
# and the progress lines print the complaint text. On a Windows console that
# defaults to cp1252 that is an immediate UnicodeEncodeError, so force UTF-8
# and degrade unencodable characters instead of crashing a scored run.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai_service.service import classify_complaint, split_departments, MAX_DEPARTMENTS
from ai_service.tests.split_holdout_set import SPLIT_HOLDOUT_SET

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "holdout_results")

# Passed as the `classification` argument under --stub-classification. Neutral
# on purpose: if this carried the real expected category, the split prompt
# would be reading its own answer key.
STUB_CLASSIFICATION = {
    "category": "other",
    "subcategory": "unspecified",
    "priority": "medium",
    "confidence": 0.0,
    "location_text": None,
    "summary": "Placeholder classification (--stub-classification).",
    "source": "stub",
}


def _as_multiset(departments: list) -> Counter:
    """(category, priority) multiset. Order-insensitive by design; a multiset
    rather than a set so that two same-labeled departments in one complaint
    don't silently collapse into one."""
    return Counter((d.get("category"), d.get("priority")) for d in departments)


def _categories_only(departments: list) -> Counter:
    return Counter(d.get("category") for d in departments)


_PRIORITY_SEVERITY = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def _priority_comparison(expected: list, got: list):
    """Per-department priority scoring, which needs its own pairing rule
    because a split answer is a SET — unlike Phase 1, where one expected
    priority lines up with one returned priority, here the two lists can
    differ in length and order.

    Departments are paired by CATEGORY, and only categories present on both
    sides are comparable: if the model returned a department that was not
    expected at all, its priority has nothing to be right or wrong against,
    and counting it would conflate a splitting error with a priority error.
    Within a category that appears more than once, both sides are sorted by
    severity before zipping, so the pairing is deterministic.

    Returns (matched, over_escalated, under_escalated, comparable).
    """
    exp_by_cat, got_by_cat = defaultdict(list), defaultdict(list)
    for d in expected:
        exp_by_cat[d.get("category")].append(d.get("priority"))
    for d in got:
        got_by_cat[d.get("category")].append(d.get("priority"))

    matched = over = under = comparable = 0
    for cat in set(exp_by_cat) & set(got_by_cat):
        key = lambda p: _PRIORITY_SEVERITY.get(p, -1)  # noqa: E731
        for ep, gp in zip(sorted(exp_by_cat[cat], key=key), sorted(got_by_cat[cat], key=key)):
            comparable += 1
            if ep == gp:
                matched += 1
            elif key(gp) > key(ep):
                over += 1
            else:
                under += 1
    return matched, over, under, comparable


def _truncate(text: str, length: int = 56) -> str:
    text = " ".join(text.split())
    return text if len(text) <= length else text[: length - 1] + "…"


def _mark_for(row: dict) -> str:
    if row["source"] == "error":
        return "!"
    if row["fallback"]:
        return "-"
    if row["exact_ok"]:
        return "OK"
    if row["count_ok"]:
        return "~"    # right number of departments, wrong labels
    if row["over_split"]:
        return "^"    # split something that should not have been split
    if row["under_split"]:
        return "v"    # failed to split something that should have been
    return "X"


def run_case(case: dict, stub: bool) -> dict:
    expected = case["expected_departments"]
    expected_ms = _as_multiset(expected)
    alt = case.get("also_accept_departments")
    alt_ms = _as_multiset(alt) if alt else None

    try:
        classification = STUB_CLASSIFICATION if stub else classify_complaint(case["text"])
        result = split_departments(case["text"], classification)
    except Exception as exc:  # noqa: BLE001 — one bad case must not kill the run
        return {
            "text": case["text"], "lang": case.get("lang"), "tags": case.get("tags", []),
            "note": case.get("note"), "borderline": bool(case.get("borderline")),
            "expected_departments": expected, "got_departments": [],
            "expected_count": len(expected), "got_count": 0,
            "exact_ok": False, "count_ok": False, "category_set_ok": False,
            "split_decision_ok": False, "over_split": False, "under_split": False,
            "matched": 0, "recall": 0.0, "precision": 0.0,
            "priority_matched": 0, "priority_over": 0, "priority_under": 0, "priority_comparable": 0,
            "exceeded_cap": False, "is_split_consistent": True,
            "source": "error", "fallback": True, "error": str(exc),
        }

    got = result.get("departments", [])
    got_ms = _as_multiset(got)
    is_fallback = bool(result.get("fallback"))

    exact_ok = got_ms == expected_ms or (alt_ms is not None and got_ms == alt_ms)
    count_ok = len(got) == len(expected)
    category_set_ok = _categories_only(got) == _categories_only(expected)

    expected_is_split = len(expected) > 1
    got_is_split = bool(result.get("is_split"))

    matched = sum((got_ms & expected_ms).values())
    p_matched, p_over, p_under, p_comparable = _priority_comparison(expected, got)

    return {
        "text": case["text"], "lang": case.get("lang"), "tags": case.get("tags", []),
        "note": case.get("note"), "borderline": bool(case.get("borderline")),
        "expected_departments": expected,
        "got_departments": got,
        "expected_count": len(expected),
        "got_count": len(got),
        "exact_ok": exact_ok,
        "count_ok": count_ok,
        "category_set_ok": category_set_ok,
        "split_decision_ok": expected_is_split == got_is_split,
        "over_split": len(got) > len(expected),
        "under_split": len(got) < len(expected),
        "matched": matched,
        "recall": matched / len(expected) if expected else 0.0,
        "precision": matched / len(got) if got else 0.0,
        "priority_matched": p_matched,
        "priority_over": p_over,
        "priority_under": p_under,
        "priority_comparable": p_comparable,
        # Structural invariants the code is supposed to guarantee — checked
        # here rather than assumed, since a regression in
        # _validate_split_departments() would show up as a scoring anomaly
        # that is otherwise easy to misread as a model problem.
        "exceeded_cap": len(got) > MAX_DEPARTMENTS,
        "is_split_consistent": got_is_split == (len(got) > 1),
        "source": result.get("source", "?"),
        "fallback": is_fallback,
        "error": None,
    }


def _pct(n: int, d: int) -> str:
    return f"{n / d * 100:5.1f}%" if d else "    -"


def report(rows: list, stub: bool) -> dict:
    line = "-" * 78
    print("\n" + "=" * 78)
    print("SPLIT-DEPARTMENTS SCORECARD" + ("  (--stub-classification: component test only)" if stub else ""))
    print("=" * 78)

    errors = [r for r in rows if r["source"] == "error"]
    fallbacks = [r for r in rows if r["fallback"] and r["source"] != "error"]
    scored = [r for r in rows if not r["fallback"] and r["source"] != "error"]

    print(f"\nScored {len(scored)} of {len(rows)} cases   "
          f"(excluded: {len(fallbacks)} fallback, {len(errors)} error)")

    if not scored:
        print("\nNothing was scored — every call fell back or errored.")
        if fallbacks:
            print("If build_split_departments_prompt() is still the NotImplementedError")
            print("stub, this is expected: the prompt is Person A's deliverable and")
            print("split_departments() takes the fallback path until it lands.")
        print("Check your API key and rate limits, then re-run.")
        return {"scored": 0, "total": len(rows), "fallbacks": len(fallbacks), "errors": len(errors)}

    n = len(scored)
    exact = sum(r["exact_ok"] for r in scored)
    counts = sum(r["count_ok"] for r in scored)
    catset = sum(r["category_set_ok"] for r in scored)
    splitdec = sum(r["split_decision_ok"] for r in scored)

    p_match = sum(r["priority_matched"] for r in scored)
    p_over = sum(r["priority_over"] for r in scored)
    p_under = sum(r["priority_under"] for r in scored)
    p_total = sum(r["priority_comparable"] for r in scored)

    print(f"\n  SPLIT DECISION ok    {splitdec:>3}/{n:<4}{_pct(splitdec, n)}   (split vs no-split, ignoring labels)")
    print(f"  DEPARTMENT COUNT ok  {counts:>3}/{n:<4}{_pct(counts, n)}")
    print(f"  CATEGORY SET ok      {catset:>3}/{n:<4}{_pct(catset, n)}   (right departments, priority ignored)")
    print(f"  PRIORITY ok          {p_match:>3}/{p_total:<4}{_pct(p_match, p_total)}   (per department, over the {p_total} correctly-identified ones)")
    print(f"  EXACT MATCH          {exact:>3}/{n:<4}{_pct(exact, n)}   <-- headline")

    print("\n" + line)
    print("PRIORITY ERRORS   (per department, not per case)")
    print(line)
    print("  Scored only over departments the model identified correctly — a")
    print("  priority on a department that should not exist has nothing to be")
    print("  wrong against, and counting it would mix splitting errors into this.")
    print(f"\n  correct           {p_match:>3}/{p_total:<4}{_pct(p_match, p_total)}")
    print(f"  OVER-escalated    {p_over:>3}/{p_total:<4}{_pct(p_over, p_total)}   (floods officers with false alarms)")
    print(f"  UNDER-escalated   {p_under:>3}/{p_total:<4}{_pct(p_under, p_total)}   (a real emergency treated as routine)")
    if p_over or p_under:
        moves = Counter()
        for r in scored:
            exp_by_cat, got_by_cat = defaultdict(list), defaultdict(list)
            for d in r["expected_departments"]:
                exp_by_cat[d["category"]].append(d["priority"])
            for d in r["got_departments"]:
                got_by_cat[d["category"]].append(d["priority"])
            key = lambda p: _PRIORITY_SEVERITY.get(p, -1)  # noqa: E731
            for cat in set(exp_by_cat) & set(got_by_cat):
                for ep, gp in zip(sorted(exp_by_cat[cat], key=key), sorted(got_by_cat[cat], key=key)):
                    if ep != gp:
                        moves[(cat, ep, gp)] += 1
        print("\n  Most common misses (department: wanted -> got):")
        for (cat, ep, gp), cnt in moves.most_common(8):
            direction = "OVER" if _PRIORITY_SEVERITY.get(gp, -1) > _PRIORITY_SEVERITY.get(ep, -1) else "under"
            print(f"    {cat:<14} {ep:>8} -> {gp:<8} x{cnt}   ({direction})")

    non_borderline = [r for r in scored if not r["borderline"]]
    if len(non_borderline) != n:
        nb = sum(r["exact_ok"] for r in non_borderline)
        print(f"\n  Excluding the {n - len(non_borderline)} borderline cases:   "
              f"{nb}/{len(non_borderline)}   {_pct(nb, len(non_borderline))}")

    # ---- the metric that decides shippability -------------------------
    print("\n" + line)
    print("OVER-SPLIT vs UNDER-SPLIT   (over-splitting is the costlier failure)")
    print(line)
    over = [r for r in scored if r["over_split"]]
    under = [r for r in scored if r["under_split"]]
    single = [r for r in scored if r["expected_count"] == 1]
    multi = [r for r in scored if r["expected_count"] > 1]
    false_splits = [r for r in single if r["got_count"] > 1]

    print(f"  over-split    {len(over):>3}/{n:<4}{_pct(len(over), n)}   returned MORE departments than expected")
    print(f"  under-split   {len(under):>3}/{n:<4}{_pct(len(under), n)}   returned FEWER departments than expected")
    print(f"\n  FALSE SPLIT RATE   {len(false_splits)}/{len(single)}   {_pct(len(false_splits), len(single))}")
    print("    (single-department complaints wrongly split — dispatches two")
    print("     teams to one problem; the design spec's costliest error)")
    if multi:
        missed = sum(1 for r in multi if r["got_count"] == 1)
        print(f"\n  MISSED SPLIT RATE  {missed}/{len(multi)}   {_pct(missed, len(multi))}")
        print("    (multi-department complaints collapsed to a single department)")

    # ---- trap cases ----------------------------------------------------
    traps = [r for r in scored if "causation_trap" in r["tags"] or "symptom_trap" in r["tags"]]
    if traps:
        print("\n" + line)
        print("TRAP CASES   (must NOT split — root-cause department only)")
        print(line)
        for kind in ("causation_trap", "symptom_trap"):
            group = [r for r in traps if kind in r["tags"]]
            if group:
                held = sum(1 for r in group if r["got_count"] == 1)
                print(f"  {kind:<16} held {held}/{len(group)}   {_pct(held, len(group))}")
        broke = [r for r in traps if r["got_count"] > 1]
        if broke:
            print("\n  Traps that over-split:")
            for r in broke:
                got = ", ".join(f"{c}/{p}" for c, p in _as_multiset(r["got_departments"]).elements())
                print(f"    [{r['lang']}] {_truncate(r['text'], 52)}")
                print(f"        wanted 1 dept, got {r['got_count']}: {got}")

    # ---- max-limit cases -----------------------------------------------
    maxlimit = [r for r in scored if "max_limit" in r["tags"]]
    if maxlimit:
        print("\n" + line)
        print(f"MAX-LIMIT CASES   (5+ issues present, must cap at {MAX_DEPARTMENTS})")
        print(line)
        capped = sum(1 for r in maxlimit if r["got_count"] == MAX_DEPARTMENTS)
        print(f"  capped correctly  {capped}/{len(maxlimit)}   {_pct(capped, len(maxlimit))}")
        for r in maxlimit:
            got = ", ".join(f"{c}/{p}" for c, p in _as_multiset(r["got_departments"]).elements())
            # Distinguish keeping the WRONG departments from keeping the right
            # ones with a priority off — only the former is a truncation
            # failure, and conflating them makes the cap look broken when it
            # is not.
            if r["exact_ok"]:
                flag = ""
            elif r["category_set_ok"]:
                flag = "   <-- right 4 kept, priority off"
            elif r["got_count"] == MAX_DEPARTMENTS:
                flag = "   <-- WRONG 4 kept"
            else:
                flag = "   <-- wrong count"
            print(f"    [{r['lang']}] got {r['got_count']}: {got}{flag}")

    # ---- structural invariants ------------------------------------------
    cap_violations = [r for r in scored if r["exceeded_cap"]]
    inconsistent = [r for r in scored if not r["is_split_consistent"]]
    if cap_violations or inconsistent:
        print("\n" + line)
        print("!! STRUCTURAL INVARIANT VIOLATIONS — this is a CODE bug, not a model miss")
        print(line)
        if cap_violations:
            print(f"  {len(cap_violations)} case(s) returned more than {MAX_DEPARTMENTS} departments —")
            print("    _validate_split_departments() should make this impossible.")
        if inconsistent:
            print(f"  {len(inconsistent)} case(s) where is_split disagrees with len(departments).")

    # ---- per-language ----------------------------------------------------
    print("\n" + line)
    print("BY LANGUAGE")
    print(line)
    by_lang = defaultdict(list)
    for r in scored:
        by_lang[r["lang"] or "?"].append(r)
    print(f"  {'lang':<10}{'n':>4}{'split-dec':>12}{'exact':>10}{'false-split':>14}")
    for lang in sorted(by_lang):
        g = by_lang[lang]
        sing = [r for r in g if r["expected_count"] == 1]
        fs = sum(1 for r in sing if r["got_count"] > 1)
        print(f"  {lang:<10}{len(g):>4}{_pct(sum(r['split_decision_ok'] for r in g), len(g)):>12}"
              f"{_pct(sum(r['exact_ok'] for r in g), len(g)):>10}{_pct(fs, len(sing)):>14}")

    # ---- misses -----------------------------------------------------------
    misses = [r for r in scored if not r["exact_ok"]]
    if misses:
        print("\n" + line)
        print("ALL MISSES IN DETAIL")
        print(line)
        for r in misses:
            want = ", ".join(f"{d['category']}/{d['priority']}" for d in r["expected_departments"])
            got = ", ".join(f"{d['category']}/{d['priority']}" for d in r["got_departments"]) or "(none)"
            print(f"\n  [{r['lang']}] {_truncate(r['text'], 60)}")
            print(f"    want ({r['expected_count']}): {want}")
            print(f"    got  ({r['got_count']}): {got}")
            if r["borderline"]:
                print("    (borderline case)")
            if r["note"]:
                print(f"    label reason: {_truncate(r['note'], 110)}")

    print("\n" + line)
    print("PROVIDER MIX")
    print(line)
    for src, cnt in Counter(r["source"] for r in scored).items():
        print(f"  {src:<10} {cnt}")

    return {
        "scored": n, "total": len(rows), "fallbacks": len(fallbacks), "errors": len(errors),
        "exact_accuracy": exact / n,
        "split_decision_accuracy": splitdec / n,
        "department_count_accuracy": counts / n,
        "category_set_accuracy": catset / n,
        "priority_accuracy": p_match / p_total if p_total else None,
        "priority_comparable": p_total,
        "priority_over_escalated": p_over,
        "priority_under_escalated": p_under,
        "over_split_count": len(over), "under_split_count": len(under),
        "false_split_rate": len(false_splits) / len(single) if single else None,
        "missed_split_rate": (sum(1 for r in multi if r["got_count"] == 1) / len(multi)) if multi else None,
        "mean_recall": sum(r["recall"] for r in scored) / n,
        "mean_precision": sum(r["precision"] for r in scored) / n,
        "cap_violations": len(cap_violations),
        "is_split_inconsistencies": len(inconsistent),
        "stub_classification": stub,
        "provider_mix": dict(Counter(r["source"] for r in scored)),
    }


def main():
    parser = argparse.ArgumentParser(description="Score split_departments() against the Phase 3 held-out set.")
    parser.add_argument("--start", type=int, default=0, help="skip the first N cases")
    parser.add_argument("--limit", type=int, default=None, help="only run N cases")
    parser.add_argument("--delay", type=float, default=15.0,
                        help="seconds between calls (default 15 for free-tier limits)")
    parser.add_argument("--stub-classification", action="store_true",
                        help="pass a neutral placeholder classification instead of calling "
                             "classify_complaint() first (halves API calls; component test, not production path)")
    parser.add_argument("--set", choices=["25", "100"], default="100",
                        help="which holdout set to score (default: the 100-case set)")
    args = parser.parse_args()

    if args.set == "100":
        from ai_service.tests.split_holdout_set_100 import SPLIT_HOLDOUT_SET_100 as chosen_set
    else:
        chosen_set = SPLIT_HOLDOUT_SET

    cases = chosen_set[args.start:]
    if args.limit:
        cases = cases[: args.limit]

    calls_per_case = 1 if args.stub_classification else 2
    total_calls = len(cases) * calls_per_case
    print(f"\nRunning {len(cases)} split-holdout cases"
          f"{' (stubbed classification)' if args.stub_classification else ' (classify -> split)'},"
          f" {args.delay:g}s between calls ({total_calls} calls total).")
    print(f"Estimated runtime: ~{(total_calls * args.delay) / 60:.0f} minutes. Progress prints as it goes.\n")

    rows = []
    os.makedirs(RESULTS_DIR, exist_ok=True)
    partial_path = os.path.join(RESULTS_DIR, "_split_partial.json")

    for i, case in enumerate(cases):
        if i > 0:
            time.sleep(args.delay * calls_per_case)

        row = run_case(case, args.stub_classification)
        rows.append(row)

        with open(partial_path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)

        print(f"  [{args.start + i + 1:>2}/{args.start + len(cases)}] {_mark_for(row):<2} "
              f"({row['expected_count']}->{row['got_count']}) {_truncate(case['text'], 48)}")

    summary = report(rows, args.stub_classification)

    suffix = f"_{args.set}" + ("_stub" if args.stub_classification else "")
    out_path = os.path.join(RESULTS_DIR, f"split_holdout{suffix}.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, ensure_ascii=False, indent=2)
    if os.path.exists(partial_path):
        os.remove(partial_path)

    print(f"\nFull results saved to: {out_path}")
    print("Commit this file. After any prompt or example change, re-run and")
    print("diff the two — that's how you tell an improvement from a regression.\n")


if __name__ == "__main__":
    main()
