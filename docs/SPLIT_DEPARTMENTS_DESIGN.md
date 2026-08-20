# Split-Departments Design Spec (Phase 3)

This is the design memory for `split_departments(text, classification)` —
multi-department complaint splitting. Same convention as
`CLASSIFICATION_DESIGN.md`: rules here are testable constraints, not prompt
wording, and any implementation (`prompts.py`, `examples.py`, holdout set)
gets built *from this document*.

Status: contract locked 2026-08-20. Person A owns filling in the actual
splitting rubric (§2+) before implementation starts.

---

## 1. Output contract — LOCKED, do not change without updating backend same-day

```python
split_departments(text: str, classification: dict) -> dict
```

`classification` is the dict already returned by `classify_complaint()` for
this same `text` — the function decides whether that single classification
should be broken into multiple department-routed pieces.

Returns:

```json
{
  "is_split": true,
  "departments": [
    {
      "category": "roads",
      "subcategory": "pothole",
      "priority": "high",
      "confidence": 0.85,
      "excerpt": "large pothole on MG road causing accidents",
      "location_text": "MG Road near signal"
    },
    {
      "category": "garbage",
      "subcategory": "overflow",
      "priority": "medium",
      "confidence": 0.78,
      "excerpt": "garbage bin overflowing nearby",
      "location_text": "MG Road near signal"
    }
  ],
  "source": "gemini",
  "fallback": false
}
```

**Rules:**

1. **`departments` is always a non-empty list, never empty.** A
   single-department complaint returns `is_split: false` with `departments`
   as a 1-item list containing the original classification reshaped into the
   per-department item format. Backend always iterates `departments` the
   same way regardless of split count — there is no separate "no split" code
   path.
2. **`is_split` is a separate bool**, not derived from list length at the
   call site, so backend can log/monitor split rate directly.
3. **Max 4 departments per complaint.** A complaint that appears to need
   more than 4 should be capped at the 4 most severe/distinct issues rather
   than emitting a 5th+ item — revisit this ceiling once holdout data exists,
   but ship with it.
4. **Each department item is self-contained**, including its own
   `location_text` — even though it will usually be identical across items
   for one complaint (same street, two problems). Items are never allowed to
   reference a shared top-level location field.
5. **`excerpt`** is the text slice that justified that department's split —
   gives a human reviewer something to check per sub-item, same rationale as
   `CLASSIFICATION_DESIGN.md`'s reasoning-before-labels principle.
6. **Failure/fallback behavior:** on any error (timeout, parse failure,
   provider exhaustion), return `is_split: false`, `departments:
   [<classification unchanged, reshaped into item format>]`, `source:
   "fallback"`, `fallback: true`. A failed *split* is not a failed
   *classification* — do not force confidence to 0 the way an
   out-of-taxonomy category answer does. Backend sees `fallback: true` and
   knows split-detection didn't run, but the original single-department
   routing is still trustworthy.
7. **Reliability contract matches Phase 1**: timeout, retry, two-provider
   chain (Gemini → Groq) before falling back, per rule 6. Never raises.

---

## 2. Splitting rubric

**Core principle — bias against over-splitting.** A false-positive split
wastes multiple departments' time dispatching on one issue; a false-negative
(under-split) only costs one department fixing something slightly outside
its lane. When a case is ambiguous, don't split.

### A. Rule coverage matrix

10 load-bearing rules, covered across 20 holdout slots by mixing traps and
multi-issue combinations. R3/R4/R9 describe properties of the model's
*live output* — verified by inspecting real `split_departments()` results
during scoring, not something ground truth encodes (see §3's generation
constraints: confidence/excerpt/location_text are deliberately absent from
`expected_departments`, since they're not labelable facts).

| # | Rule | Slots |
|---|------|-------|
| R1 | **Max-4 limit.** A complaint with 5+ issues is capped at the 4 most severe/distinct — matches §1 rule 3. Ground truth: `expected_departments` capped at 4. | 20 |
| R2 | **No-split baseline.** A single-issue complaint: `expected_departments` has exactly 1 item; there is no separate `expected_is_split` field — the scorer derives it from count, same as `_validate_split_departments()` does. | 1, 2, 3 |
| R3 | **Excerpt justification.** Every live-output item's `excerpt` should be a verbatim substring of the input text — audited on real runs, not labeled in ground truth. | N/A (runtime audit only) |
| R4 | **Independent locations.** Every live-output item carries its own `location_text`, even when identical across items (e.g. both "MG Road") — matches §1 rule 4. Not labeled in ground truth. | N/A (runtime audit only) |
| R5 | **Independent priority.** Priority is not inherited from `classification`. A high-priority roads issue and a low-priority parks issue in the same text are judged independently, per `CLASSIFICATION_DESIGN.md` §2's priority framework. | 9, 11, 14, 16 |
| R6 | **Symptom trap (no split).** A blocked drain (`drainage`) leaving a mess on the road does not split into `sanitation` — the root fix is drainage. Mirrors `CLASSIFICATION_DESIGN.md`'s "pick the department that does the actual physical fix" rule. | 6, 7 |
| R7 | **Cross-causation trap (no split).** A burst pipe (`water_supply`) washing out a footpath (`roads`) does not split — route to the underlying-cause owner. Same rule as `CLASSIFICATION_DESIGN.md`'s water-pipe/road-damage boundary ruling. | 4, 5, 8 |
| R8 | **Obvious split.** Unrelated issues needing separate physical dispatch (e.g. dead streetlight + overflowing garbage bin). | 10, 12, 13, 15 |
| R9 | **Independent confidence.** Live-output confidence is scored per sub-item, not copied from the main classification or a sibling item — one obvious issue can be 0.95 while an ambiguous secondary issue sits at 0.60. Not labelable in ground truth (confidence is the model's self-assessment). | N/A (runtime audit only) |
| R10 | **Fallback contract.** Failure/error behavior is §1 rule 6 — tested at the pipeline (service.py) level, not encoded as a holdout case. | pipeline-level only |

### B. Distribution matrix

| Slots | Split profile | Target scenario | Rules exercised | Language/script |
|---|---|---|---|---|
| 1-3 | No split (baseline) | Standard single issue (e.g. just a pothole) | R2, R3, R4 | Romanized (Hinglish), Tamil |
| 4-5 | No split (causation trap) | Pipe broke the road → route purely to `water_supply` | R2, R7 | Clean English, Kannada |
| 6-8 | No split (symptom trap) | Drain overflowing smells bad → route purely to `drainage` | R2, R6 | Native (Telugu, Hindi) |
| 9-11 | 2-way (independent priority) | Live wire (critical) + broken bin lid (low) | R3, R4, R5 | Clean English, Bengali |
| 12-15 | 2-way (obvious split) | Streetlight out + missed garbage collection | R4, R8 | Romanized (Hinglish) |
| 16-17 | 3-way (standard) | Tree blocking road + sparking wire + dead dog | R4, R5, R8 | Clean English |
| 18-19 | 3-way (confidence variance) | 1 obvious issue (high conf) + 2 ambiguous (mid conf) | R4, R9 | Native (Marathi) |
| 20 | 4-way (max limit) | Major storm damage listing 5+ distinct department issues | R1, R3, R8 | Romanized (Hinglish) |

Tallies: 8 no-split, 7 two-way, 4 three-way, 1 four-way (sum 20). Trap
density: 5 bias-against-over-splitting traps (slots 4-8). Language mix: 6
clean English, 7 romanized/code-mixed, 7 native script (sum 20).

## 3. Holdout set design (Person C)

This is ground-truth data for blind-scoring `split_departments()` output —
**never shown to the model, never copied into `examples.py`**, same hard
rule as the Phase 1 holdout set (`holdout_set.py`'s own docstring: "the
moment a case appears in the prompt, it stops being a valid held-out test").
Follow `holdout_set.py`'s flat `expected_*` field convention, not
`examples.py`'s `{"text", "output"}` model-facing wrapper — a holdout case
is a labeled test input, not a demonstration fed to the model.

### C. Generation rulebook

Objective: draft 20 blind-labeled holdout cases for a new
`ai_service/tests/split_holdout_set.py`, covering the rule/distribution
matrices in §2.A/§2.B above.

**Schema — ground truth, not model output.** No `output` wrapper, no
`reasoning`, no `is_split`/`source`/`fallback` keys — those are either
computed by the scorer (`is_split` derives from `len(expected_departments) >
1`, same principle `_validate_split_departments()` uses in `service.py`) or
don't apply to ground truth at all (`source`/`fallback` describe pipeline
behavior, not a label; `reasoning` is only useful when shown to the model,
which a holdout case never is).

```python
{
    "text": "<the complaint, native script preserved as-is>",
    "expected_departments": [
        {"category": "roads", "priority": "high"},
        {"category": "garbage", "priority": "medium"},
    ],
    "note": "<why this label, in the labeler's own words — required, especially for the trap slots 4-8: state explicitly why it did NOT split>",
    "lang": "en",
    "tags": ["obvious_split"],  # or ["no_split", "causation_trap"], ["symptom_trap"], ["max_limit"], etc.
}
```

A no-split case is `expected_departments` with exactly 1 item — never an
empty list, never a separate `expected_is_split` field (the scorer derives
it, same as the code does).

Generation constraints:

- **Bias against over-splitting.** If one issue is merely a symptom of
  another (e.g. a pothole filled with trash), the correct label is 1
  department, not 2. `note` must state the root-cause department and why
  the symptom doesn't get its own entry.
- **Independent priority per item.** Don't let `expected_departments`
  inherit one blanket priority — label each sub-issue's priority against
  `CLASSIFICATION_DESIGN.md` §2 independently, same discipline as R5/R9.
- **No confidence, no excerpt, no location_text in ground truth.**
  Confidence is the model's own self-assessment, not a labelable fact.
  Excerpt/location extraction is real but too string-fragile to score by
  exact match — the scorer (§ below) only checks department count and
  per-department category/priority, mirroring how the Phase 1 scorer never
  scores `summary`/`location_text`/`confidence` exactness either.
- **Blind labeling.** Label from independent municipal judgment, same as
  `holdout_set.py` — do not look at Person A's `build_split_departments_prompt()`
  or few-shot examples while writing these.
- **Language authenticity**, per the distribution matrix's language column.

### D. Audit checklist

Human reviewers check structural constraints, not subjective "goodness":

- [ ] **Schema strictness.** Does each case have exactly `text`,
      `expected_departments`, `note`, `lang`, `tags` — no invented
      `is_split`/`source`/`fallback`/`output` keys? (Those don't belong in
      ground truth.)
- [ ] **List integrity.** Is `expected_departments` populated with at least
      1 item in every case, including no-split cases?
- [ ] **Max-4 enforcement.** For slot 20, does `expected_departments` cap at
      4 items rather than listing a 5th+?
- [ ] **Trap success.** For slots 4-8, does `expected_departments` have
      exactly 1 item (the root-cause department), and does `note` state why
      the symptom/downstream issue doesn't get its own entry?
- [ ] **Location independence is N/A here** — ground truth doesn't carry
      `location_text` at all (see generation constraints); this is scored
      structurally in `_validate_split_departments()`'s output instead.
- [ ] **Priority independence.** For slots 9-11, do the sub-items carry
      genuinely different `priority` values (e.g. `critical` and `low`), not
      a copy of what the single-classification priority would have been?
- [ ] **No overlap with `examples.py`.** None of these 20 texts (or close
      paraphrases) may appear in Person A's few-shot set — check both ways
      once both are written.

## 4. Few-shot examples — TODO (Person A)

Separate, independently-authored set for `build_split_departments_prompt()`
— must not share any text with §3's holdout cases. Model-facing schema
(what the model is actually asked to produce) is `{"reasoning": ...,
"departments": [...]}`, no `is_split`/`source`/`fallback`, per §1's division
of labor between what the model predicts and what `service.py` computes.

## 5. Known failure modes — TODO (fill in once holdout data exists)
