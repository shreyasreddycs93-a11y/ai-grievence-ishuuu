# Classification Design Spec

This is the design memory for the classification layer (`category`, `priority`,
`confidence`), independent of any particular `prompts.py` / `examples.py` /
`holdout_set.py` implementation. When those three files get rebuilt from
scratch, they get rebuilt *from this document* — every rule below was learned
the hard way (a regression, a misclassified holdout case, or a validator bug
caught in review) and re-deriving it from nothing would repeat the same
mistakes.

Each rule below is stated as a testable constraint, not as prompt wording —
the next implementation is free to phrase it however scores best, as long as
the behavior it produces satisfies the rule.

---

## 1. Category framework

**Core principle: pick the category that owns the FIX — whichever real
municipal team would actually be dispatched — never whichever category's
keyword happens to appear in the complaint text.** This is a department-
routing decision, not a topic-tagging decision.

### The 9 categories

| Category | Owns |
|---|---|
| `water_supply` | Drinking/piped water: no supply, low pressure, leaks, contamination, broken taps, meters, borewells. |
| `roads` | The road/footpath surface and anything obstructing it: potholes, cave-ins, cracks, encroachments blocking passage, debris, a fallen tree or structure blocking a road. |
| `sanitation` | Cleaning **services** for public spaces and facilities — street sweeping, public toilet upkeep, whether an area is being kept clean. About whether a service is being performed, not about waste itself. |
| `electricity` | Power supply and electrical equipment — outages, voltage problems, transformers, poles, wires, meters. |
| `streetlights` | Public lighting specifically — non-functional, damaged, or missing streetlights. |
| `drainage` | Stormwater and sewage infrastructure — drains, manholes, culverts, waterlogging, sewage overflow or contamination. |
| `garbage` | Solid waste — bins, missed collection, illegal dumping, waste accumulation, anything that needs to be physically hauled away. |
| `parks` | The public park/green-space asset itself — playground equipment, park furniture, landscaping, gates, fixtures. |
| `other` | Anything that doesn't fit above: private-property disputes, general feedback, unexplained phenomena, staff conduct, unregulated/unlicensed activity, complaints spanning departments with no clear single owner. |

### Boundary rulings (each one caught a real mislabel — treat as load-bearing)

- **`sanitation` is a service failure, not a waste problem.** "Street sweepers don't come on time" is sanitation. A dead rat on the stairs is *not* sanitation — see next rule.
- **`garbage` includes carcasses.** A dead animal needs physical removal like any other waste, even though it isn't literally trash. Dead-rat-on-a-footbridge and dead-dog-near-a-water-tank are both `garbage`, not `sanitation`. (Regression risk: the model has been observed defaulting these to `sanitation` because "cleanup" sounds like a cleaning-service word — it isn't, it's a haulage job.)
- **A tree (or branch) is categorized by what it threatens, not by being a tree.** A tree/branch blocking or endangering a road is `roads`. A tree/branch that is itself the park asset in question (e.g. routine park landscaping) is `parks`. The determining question is "what does this complaint need fixed" — the road, or the park.
- **Vegetation from private property spilling into public space is `other`, not `parks`.** The parks department doesn't own or maintain private gardens; a complaint about a neighbor's overgrown bougainvillea branches hanging over a wall is a private-property/nuisance matter, not a parks-asset matter.
- **Animal control has no civic-engineering owner — default to `other`.** None of the other 8 categories are staffed to catch, relocate, or manage animals. This applies to stray dogs being dangerous to pedestrians, illegal/unlicensed animal slaughter, and similar. **Nuance, not a blanket rule**: if the animal's role in the complaint is *physically obstructing a road or path* (e.g. cattle sitting in the road causing accidents), that's still `roads` under the general obstruction rule — the road is what needs to be cleared, same as if it were debris. The `other` default applies when the complaint is about the animal being dangerous/unregulated, not about it blocking a right-of-way.
- **Cross-department causation doesn't change the category** — pick the department that does the *actual physical fix*, not the one that caused the underlying problem. A road damaged by a leaking water pipe underneath it is still `roads` (Roads Dept resurfaces it), even though Water Board caused it and may need to be involved too.
- **Unlicensed/unregulated commercial activity (illegal slaughter stalls, unauthorized vending encroachments) is `other`, not the category the *symptom* resembles.** These are enforcement/licensing matters, not a cleaning-service or infrastructure failure — even when the symptom (mess, blockage) looks like it belongs to `sanitation` or `roads`.

---

## 2. Priority framework

**Core principle — hard constraint, not a preference: priority must be judged
by CONSEQUENCE (what actually happens if nobody acts), never by a literal
checklist of trigger phrases.** This is non-negotiable design history: a
narrow rules-based pass ("reserve critical for a hole you could fall into,"
etc.) was tried mid-project and **regressed priority accuracy from 80% to
73%** by making the model over-index on literal wording instead of judging
the actual danger described. Any future rubric that reads like a checklist
of required words/phrases is repeating a known failure mode — verify against
the holdout set before trusting it.

Priority also does **not** track how upset or how vivid the complaint sounds.
Capitals, insults, and exclamation marks carry no weight. A calmly-worded
live wire is critical; a furious complaint about street sweepers is low.

### The four levels, stated as consequence tests

- **`critical` — the physical-harm test.** A real chance someone is killed or
  seriously injured in the next few hours. Sparking or exposed live wires, an
  actively collapsing structure, floodwater entering an occupied/enclosed
  space, a forceful/pressurized burst strong enough to knock someone over, an
  active toxic/chemical exposure, a road hazard already causing crashes. It
  does **not** cover a hazard that's serious only after days of continued
  neglect (that's `high`), and it does not cover property/water/money damage
  with no plausible injury path (`high` at most, never `critical`).
- **`high` — the "reaches critical if ignored for days" test, OR a
  shared-resource disruption.** Two independent qualifying conditions, either
  is sufficient:
  1. A hazard that *would* become critical-level dangerous if left unaddressed
     for days — an uncovered fall-in risk, exposed-but-not-yet-live electrical
     equipment, a structural defect not yet actively harming anyone.
  2. A disruption affecting many people or a shared resource at once — a
     whole-street/area outage, an obstruction blocking a road (regardless of
     whether clearing it is quick or requires a longer legal/demolition
     process), contaminated water, or a disease/breeding risk — including one
     that hasn't yet produced a confirmed illness. Breeding risk counts on its
     own; a confirmed outbreak is not required to reach `high`.
- **`medium`** — a real, currently-occurring issue that degrades service or
  amenity, but nobody is in danger and it's contained: a freshly reported
  leak, a facility unpleasant/unsafe to use, an ordinary pothole on a
  residential/side road.
- **`low` — specific-but-trivial is still low.** Cosmetic or trivial problems
  stay low **even when the complaint names an exact location or a specific
  object** — a broken bin lid, a cracked meter glass, faded paint. Naming a
  place makes a complaint *specific*, not *serious*; these are independent
  axes and only severity moves the priority. Preventive/scheduled maintenance
  that hasn't caused a problem yet ("needs desilting before monsoon") is also
  `low`. (Regression this rule fixes: without an explicit low-tier definition
  that isn't just "vague," specific-but-minor complaints had nowhere to land
  and got defaulted up to `medium`.)

### Escalation rules that cut across levels

- **Leak/outage duration escalates over days, not hours.** A fresh report of
  an ongoing failure (a leak, an outage) that is still containable sits at the
  *lower* of two plausible levels. The same problem explicitly described as
  unaddressed for **multiple days** moves up one level — nobody has acted,
  and unaddressed is worse than freshly discovered.
- **Stated harm already occurred escalates.** An ordinary pothole/rough
  surface on a residential road stays `medium`; it only rises to `high` if the
  complaint states an accident, injury, an arterial road, or vehicles getting
  stuck. This generalizes past potholes: any complaint that explicitly states
  an accident/injury has already happened should be treated as one level
  above the same scenario without a stated incident.
- **Tie-breaker: when two adjacent levels are both defensible, pick the
  LOWER one.** Over-escalation floods officers with false alarms and buries
  real emergencies — and over-escalation, not under-escalation, is the
  measured failure mode in every scored run so far (19 of 27 priority misses
  in the last full scoring were over-escalations, not under). This tie-
  breaker is a direct countermeasure to that pattern and should not be
  loosened without new evidence that under-escalation has become the bigger
  risk.
  Precedence: the tie-break-down rule applies only when no explicit
  escalation rule has fired. A fired escalation (multi-day duration, stated
  harm already occurred) resolves the tie upward and is not cancelled by the
  tie-breaker.

---

## 3. Confidence framework

**Confidence is a routing signal (auto-act vs. send to a human), not a
measure of how serious or how clearly-written the complaint is.**

- Confidence must reflect the likelihood that **both** category and priority
  match what a trained municipal officer would choose. Judge the two
  separately, then **report the LOWER of the two scores.** Being sure of the
  department does not imply being sure of the urgency, and priority is
  reliably the harder call.
- **Cap confidence at 0.6 whenever two adjacent priority levels were both
  weighed before picking one.** That kind of disagreement is exactly what
  human review exists to settle — it must not be reported as confident.
- A vague, off-topic, or category-ambiguous complaint should score below 0.5
  rather than guess confidently. A vividly-described complaint the model is
  genuinely unsure how to rank is a **low**-confidence answer, not a high one
  just because the writing was clear.
- **Design requirement for the few-shot set, not just the instructions**: the
  example set must include genuine mid-confidence examples (roughly 0.5-0.7)
  from the very first draft, not added later once a confidence inversion is
  found in testing. If every anchor example is high-confidence, the model has
  no pattern to imitate for "I produced an answer but I'm not sure it's
  right," and confidence calibration silently collapses toward always-high
  regardless of what the instructions say. (This already happened once: two
  examples were found to be overconfident and had to be corrected after the
  fact — build the range in from the start instead of discovering the gap
  during a holdout run.)
- Sanity check to re-run on every holdout scoring: mean confidence on correct
  answers should be meaningfully higher than mean confidence on wrong
  answers. If the gap collapses to near-zero, confidence has stopped carrying
  information and the review threshold can't function no matter where it's
  set.

---

## 4. Known failure modes — regression-test against these going forward

Every future holdout run should be checked against this list specifically,
not just against an aggregate accuracy number.

1. **Invalid category strings get silently coerced to `other` and their
   confidence zeroed, with no record of what was actually returned.** This
   happens when the model invents a category outside the fixed 9 (plausibly
   things like "animal_control" or "licensing_enforcement" for exactly the
   no-clean-owner cases) — the validator catches it and defaults to `other`,
   which is directionally survivable but currently silent and unverified.
   **Fix direction: this must become structurally impossible, not patched
   after the fact** — constrain category/priority to enum values at the API
   level (e.g. `response_schema` with an enum) so an out-of-list value simply
   cannot be returned, instead of being caught and coerced downstream. Until
   that lands, any validator that coerces an invalid value must also log/
   persist the original invalid string somewhere inspectable — silent
   coercion with no trace of the original answer is itself a failure mode.
2. **Systematic over-escalation.** The dominant error pattern observed
   whenever this has been measured: routine defects (a broken paver, a
   choked storm drain, tangled overhead cables, a sunken-but-covered manhole
   frame) getting bumped one full level above their consequence-based tier.
   Track the over-escalated vs. under-escalated split on every run, not just
   the miss count — a rubric change that reduces misses but keeps the same
   lopsided ratio hasn't fixed the actual problem.
3. **garbage / sanitation / drainage boundary confusion**, specifically:
   - a dead animal miscategorized as `sanitation` instead of `garbage`
   - street sweepers dumping collected dust into a storm drain miscategorized
     as `drainage` instead of `garbage` (the fix is hauling the waste, not a
     drainage-infrastructure repair)
   - a service failure (irregular sweeping, unclean toilet) miscategorized as
     `garbage` instead of `sanitation`

---

## 5. Open refinement items — none of these are implemented yet

Carried forward as the standing to-do list; none should be assumed done in
the next build unless explicitly re-verified.

1. **System-instruction / user-content split.** The classification call
   currently concatenates the rubric, the few-shot examples, and the new
   complaint into one flat string. Splitting the stable rubric+examples
   portion into an actual system-instruction slot (separate from the
   per-request content) is what enables prompt caching — right now every
   call re-sends and presumably re-processes the entire fixed prefix.
2. **`response_schema` enum constraints on category/priority.** Directly
   closes failure mode 4.1 — makes an out-of-taxonomy answer impossible
   instead of catchable.
3. **A `reasoning` field emitted before the labels**, not after. Asking the
   model to state its reasoning ahead of committing to category/priority
   (rather than only asking for the final labels) is expected to improve
   both accuracy and auditability of individual answers, and gives a human
   reviewer something to check besides the bare label.
4. **Groq cross-check on low confidence**, not just on Gemini failure. Today
   Groq is wired purely as a failover — it only runs if Gemini raises an
   exception. It has never been used to independently re-check a
   low-confidence Gemini answer, which was the original intent. A same-input
   disagreement between two providers is itself a stronger signal for
   routing to human review than either provider's self-reported confidence
   alone.
5. **Per-language / per-script reporting as a standard, built-in part of
   scoring** — not a one-off manual analysis. Every holdout run should
   surface accuracy broken out by detected script/translation-path by
   default, the same way it already surfaces category/priority accuracy.
   The one time this breakdown was computed by hand, it reversed an
   assumption the project had been running on (native-script/translated
   cases outperformed direct Latin-script cases at 100-case scale) — that
   kind of result should be visible on every run, not discovered
   occasionally.
6. **Pick the human-review confidence threshold from real calibration data,
   not as an arbitrary constant.** The current threshold is a fixed number
   set once and never revisited. It should be chosen (and re-checked
   periodically) from the actual mean-confidence-correct vs.
   mean-confidence-wrong gap on a scored run — e.g. picking the threshold
   that maximizes caught-wrong-answers while minimizing needless review of
   correct ones, using real distribution data instead of a guess.

---

## How to use this document

When rebuilding `prompts.py`, `examples.py`, and `holdout_set.py`:

- Every rule in §1 and §2 needs at least one few-shot example and at least
  one holdout case that specifically exercises it — not as a checklist to
  copy verbatim into prompt text (see §2's hard constraint), but as a
  behavior the new implementation must produce.
- §3's mid-confidence requirement is a constraint on the *example set*
  itself, independent of instruction wording — check the confidence values
  across the rebuilt few-shot set before writing a single line of new
  rubric text.
- §4 is the regression checklist for the first holdout run against the
  rebuilt files — score specifically against these patterns, not just the
  aggregate exact-match number.
- §5 is out of scope for the prompt/example/holdout rebuild itself, but
  should stay visible so it isn't lost in the rewrite.
