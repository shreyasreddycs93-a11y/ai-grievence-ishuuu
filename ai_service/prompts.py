"""
All prompt text lives here — nowhere else in this package. If you or your
teammate refine wording with Gemini/ChatGPT, this is the only file that
should change.
"""
import json
from .examples import FEW_SHOT_EXAMPLES
from .categories import CATEGORIES, PRIORITIES

NORMALIZE_PROMPT_TEMPLATE = """You are normalizing a citizen's civic complaint for an Indian municipal grievance system.

The input text may be in English, Hindi, a regional Indian language, or Hinglish (code-mixed Hindi-English).

Task:
1. Detect the primary language of the input (use ISO-style short names like "english", "hindi", "hinglish", "kannada", etc.)
2. Rewrite the complaint in clear, simple English, preserving every factual detail (what happened, where, since when, who is affected). Do not add information that isn't in the original. Do not shorten or summarize — just translate/normalize.

Input complaint:
\"\"\"{raw_text}\"\"\"

Respond with ONLY a JSON object in this exact shape, no other text:
{{"canonical_text": "<the normalized English text>", "language": "<detected language>"}}
"""

IMAGE_DESCRIBE_PROMPT = """You are looking at a photo submitted alongside a civic complaint (e.g. a pothole, damaged pipe, garbage pile, broken streetlight, etc.) in an Indian city.

Describe factually, in one paragraph, what civic issue (if any) is visible in the image. Mention visible damage, hazards, or conditions relevant to a municipal department. Do not speculate about things not visible in the image. If the image does not show any civic issue, say so plainly.
"""

CLASSIFICATION_SYSTEM_INSTRUCTION = f"""Priority guidance:

Priority measures CONSEQUENCE, not how upset the citizen sounds. Angry capital
letters, insults, and exclamation marks carry no priority weight. A
calmly-worded live wire is critical; a furious complaint about street
sweepers is low. For each level, judge what actually happens if nobody acts.
The examples below are illustrative, not an exhaustive checklist — don't
withhold a level just because a complaint doesn't use an example's exact
words, and don't grant a level just because it echoes one. Judge the real
danger described, not the vocabulary.

- "critical": a real chance someone is killed or seriously injured in the
  next few hours. This is a physical-harm test. It covers sparking or fallen
  live wires, exposed conductors a person could touch, a structure that is
  actively collapsing or about to, floodwater actively entering an occupied
  or enclosed space, a burst forceful or pressurized enough to knock someone
  over, a toxic or chemical hazard people are being exposed to right now,
  and a road hazard already causing crashes. It does NOT cover a hazard that
  is serious but only turns dangerous after days of neglect (that's high),
  or damage to property, water, or money with no plausible injury to a
  person (high at most, never critical) — a fall-in risk needs an actual
  uncovered hole or drop, not merely a sunken or misaligned surface.
- "high": either (a) a hazard that would reach critical-level danger if
  ignored for days — an uncovered fall-in risk, exposed-but-not-yet-live
  electrical equipment, a structural defect not yet actively harming anyone
  — or (b) a disruption affecting many people or a shared resource at once:
  a whole street or area outage, an obstruction blocking a road (regardless
  of whether removing it is a quick clearing job or a longer legal or
  demolition process), contaminated water, or disease-carrying conditions —
  including a breeding or contamination risk that hasn't caused confirmed
  illness yet, not only a confirmed outbreak.
- "medium": a real, currently-occurring civic issue that degrades service or
  amenity, but nobody is in danger and it's contained — a freshly reported
  leak, a facility dirty or broken enough that it's unpleasant or unsafe to
  actually use, a pothole or rough surface on a residential or side road.
- "low": genuine but not urgent. Cosmetic or trivial problems — a broken
  lid, a cracked meter glass, droppings on a bench, a faded road marking —
  even when the complaint names an exact location; naming a place makes a
  complaint specific, not serious. Preventive or scheduled maintenance that
  hasn't caused a problem yet ("needs desilting before monsoon," "due for
  its annual clean"). And vague complaints with no specific problem, place,
  or affected person named.

Tie-breakers that cut across levels:
- Ordinary potholes and rough road surface on a residential or side road
  stay medium; they only rise to high if the complaint states accidents,
  injuries, an arterial road, or vehicles becoming stuck.
- Time changes severity for ongoing wastage or an unrepaired failure (a
  leak, an outage): a fresh report — within the last few hours, still
  containable — sits at the lower of two plausible levels. The same problem
  explicitly described as unaddressed for multiple days moves up one level
  — nobody has acted, and that's worse than something just discovered.
- If you find yourself weighing two adjacent levels, choose the LOWER one.
  Over-escalation floods officers with false alarms and buries the real
  emergencies.

Category guidance:

Pick the category that owns the FIX — whichever municipal team would actually
be dispatched — not whichever category's keyword happens to appear in the
text.

- "water_supply": drinking/piped water — no supply, low pressure, leaks,
  contamination, broken taps, meters, or borewells.
- "roads": the road or footpath surface and anything obstructing it —
  potholes, cave-ins, cracks, encroachments blocking vehicle or pedestrian
  passage, debris, or a fallen tree/structure blocking a road.
- "sanitation": cleaning SERVICES for public spaces and facilities — street
  sweeping, public toilet upkeep, an area not being kept clean. This is
  about whether a service is being performed, not about waste itself.
- "electricity": power supply and electrical equipment — outages, voltage
  problems, transformers, poles, wires, meters.
- "streetlights": public lighting specifically — non-functional, damaged,
  or missing streetlights.
- "drainage": stormwater and sewage infrastructure — drains, manholes,
  culverts, waterlogging, sewage overflow or contamination.
- "garbage": solid waste — bins, missed collection, illegal dumping, waste
  accumulation, and anything that needs to be physically hauled away,
  including a dead animal or carcass (it needs removal like any other
  waste, even though it isn't literally trash).
- "parks": PUBLIC park and green-space property itself — playground
  equipment, park furniture, landscaping, park gates and fixtures. A tree
  or plant is a "roads"/"drainage"/etc. complaint instead when the problem
  is what it's blocking or damaging, not the park asset itself. Vegetation
  from PRIVATE property spilling into public space is "other," not "parks"
  — the park department doesn't own private gardens.
- "other": anything that doesn't fit above — private-property disputes or
  encroachment, general feedback, unexplained phenomena, staff conduct, and
  complaints spanning departments with no clear primary owner.

Confidence guidance:

Confidence is the calibration signal that decides whether this answer gets
acted on automatically or gets routed to a human — it is not a measure of
how serious the complaint is or how clearly it's written.

- Return a confidence score (0.0 to 1.0) for how likely it is that BOTH your category and your priority match what a trained municipal officer would choose.
- Judge the two separately, then return the LOWER of the two scores. Being sure of the department does not make you sure of the urgency — priority is the harder call and it decides the score.
- If you weighed two adjacent priority levels before picking one, your confidence MUST be at most 0.6. That disagreement is exactly what a human reviewer is there to settle.
- If the complaint is vague, off-topic, or could belong to either of two categories, stay below 0.5 rather than guessing confidently.
- Confidence measures how likely your LABEL is correct. It does not measure how clearly the text describes a problem, how serious the problem is, or how strongly the citizen feels. A vividly described complaint you are unsure how to rank is a LOW confidence answer.
- Do not inflate confidence just because you produced an answer — an answer can be your best guess while still being uncertain.
"""

CLASSIFICATION_JSON_INSTRUCTION_TEMPLATE = """
Now classify this new complaint. Respond with ONLY a JSON object in exactly this shape, no other text, no markdown fences:
{"category": "...", "subcategory": "...", "priority": "...", "confidence": 0.0, "location_text": "..." or null, "summary": "..."}

Complaint:
\"\"\"__COMPLAINT_TEXT__\"\"\"
__IMAGE_CONTEXT__
"""


def build_classification_prompt(complaint_text: str, image_description: str | None = None) -> str:
    """Assembles the full classification prompt: system instruction + few-shot
    examples + the new complaint to classify.

    Uses plain string substitution (not str.format) because the JSON example
    embedded in the template contains literal curly braces, which would
    collide with .format()'s placeholder syntax.
    """
    examples_block = "\n\n".join(
        f"Complaint: \"\"\"{ex['text']}\"\"\"\nOutput: {json.dumps(ex['output'])}"
        for ex in FEW_SHOT_EXAMPLES
    )
    image_context = f"\nAdditional context from an attached photo: {image_description}" if image_description else ""
    final_instruction = (
        CLASSIFICATION_JSON_INSTRUCTION_TEMPLATE
        .replace("__COMPLAINT_TEXT__", complaint_text)
        .replace("__IMAGE_CONTEXT__", image_context)
    )
    return CLASSIFICATION_SYSTEM_INSTRUCTION + "\n\n" + examples_block + "\n\n" + final_instruction
