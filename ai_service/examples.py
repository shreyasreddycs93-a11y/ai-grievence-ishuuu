"""
Few-shot examples used inside the classification prompt (see prompts.py).
These are baked into every classify_complaint() call so the model has
solved examples to pattern-match against, instead of classifying cold.

REDESIGNED from scratch against the rewritten priority/category rubric in
prompts.py (see that file's "Priority guidance" / "Category guidance"
sections). Every entry below was fresh-labeled by reading only the raw
complaint text — no label was carried over from a prior version of this
file without being re-derived. Capped at 20 by deliberate choice: each
example must teach something the others don't, because every entry here
is sent on every single classification call, so redundant examples are a
pure token-cost tax with no accuracy benefit. Where two examples would
teach the same lesson, only the sharper one survives.

What this set is deliberately built to cover (one pair/anchor per lesson):
  - critical vs high water damage: a forceful/pressurized burst (critical)
    vs a passive leak explicitly unaddressed for days (high).
  - critical vs high electrical danger: actively sparking with people
    present (critical) vs exposed-but-not-yet-live equipment (high).
  - critical vs high fall-in hazard: an open, uncovered manhole (critical)
    vs a sunken-but-still-covered frame (high).
  - roads: the explicit "accident already happened" tie-breaker, a
    corrected real case showing restraint (property damage + a big pit is
    high, not automatically critical, without a stated crash), and an
    obstruction example that also teaches the category-boundary rule (a
    tree blocking a road is a ROADS complaint, not a PARKS one).
  - streetlights: a single fixture (medium) vs a whole street out for a
    week (high) — the scope tie-breaker.
  - garbage: contained/one-building (medium), a disease/breeding-risk case
    (high) — the "breeding risk counts before confirmed illness" rule —
    and a specific-but-trivial broken lid (low) — "naming a place doesn't
    make it serious."
  - sanitation: a service-quality case (medium) plus a vague one (low),
    since sanitation vs garbage was the single most confused boundary in
    holdout testing and needs its own low anchor, not a borrowed one.
  - parks: equipment damage that needs someone to interact with it to
    cause harm (medium, deliberately NOT critical/high) vs cosmetic wear
    on a still-fully-usable fixture (low).
  - other: the catch-all can still be critical (a structural collapse
    endangering the public, regardless of it being privately owned) and
    still be low (genuinely vague feedback).

Kept from the previous 17-example set (re-labeled fresh, not copied):
  pothole+accident, road-damage-from-leak, single streetlight, garbage
  1-week, mosquito/disease garbage, sparking pole, open manhole, broken
  swing, vague feedback. (10 kept, including the roads-from-leak case
  whose priority was corrected from critical to high on this pass.)

Dropped from the previous set as redundant once the above pairs existed
(kept as a design note, not silently lost): MG Road pipe-burst high (redundant
with the new critical/high water pair), "no supply for days, whole
building" high (generic shared-resource high, same lesson as the
whole-street streetlights case), a second sparking-transformer high
("sparked last night" — subtler than, and largely covered by, the
unfenced-transformer high case), a second recurring-hazard drainage high
(the sunken-frame case already anchors drainage's high tier), a second
leaning-pole streetlights high (same "hazard-if-ignored" lesson the
sunken-frame and unfenced-transformer cases already teach), and two
redundant vague/low anchors (water_supply "water problem", roads "roads
are generally bad") — one vague/low anchor (other) is enough to teach the
generalizable pattern.

Known coverage gaps NOT filled here by design (budget), tracked instead by
dedicated cases in tests/holdout_set.py: a dead-animal-carcass-is-garbage-
not-sanitation anchor, and a private-property-vegetation-is-"other"-not-
"parks" anchor. If either boundary starts showing up as a real error
pattern in holdout runs, promote one of those holdout cases into this file
(as a freshly-written example, never copied verbatim) and drop something
else to stay at 20.

Keep this list realistic and varied. If you or your teammate refine these
with Gemini/ChatGPT, replace the whole list — don't hand-edit piecemeal,
since the prompt is tuned against the set as a whole.
"""

FEW_SHOT_EXAMPLES = [
    # water_supply / critical — forceful, pressurized burst is an injury
    # risk, not just wastage. Pairs with the leak case below.
    {
        "text": "Underground pipeline achanak phat gayi hai aur paani fountain ki tarah zor se sadak par uchhal raha hai, log gir sakte hai",
        "output": {
            "category": "water_supply",
            "subcategory": "pipe_burst",
            "priority": "critical",
            "confidence": 0.85,
            "location_text": None,
            "summary": "An underground pipeline has burst and water is shooting forcefully across the road like a fountain — bystanders could be knocked over.",
        },
    },
    # water_supply / high — a passive leak explicitly unaddressed for
    # days. Contrast with the critical case above: same root problem
    # (a leak), different severity because of force, not volume.
    {
        "text": "Ghar ke bahar ki pipeline 4 din se leak ho rahi hai, bahut paani waste ho raha hai lekin koi theek karne nahi aaya",
        "output": {
            "category": "water_supply",
            "subcategory": "unrepaired_leak",
            "priority": "high",
            "confidence": 0.78,
            "location_text": "outside the house",
            "summary": "A pipeline leak outside the house has gone unrepaired for four days, wasting a large amount of water.",
        },
    },
    # roads / high — the explicit tie-breaker: an ordinary pothole becomes
    # high once the complaint states an accident already happened.
    {
        "text": "Sadak me bahut bada gadda hai, do din pehle scooter gir gaya tha kisi ka.",
        "output": {
            "category": "roads",
            "subcategory": "pothole",
            "priority": "high",
            "confidence": 0.88,
            "location_text": None,
            "summary": "Large pothole reported; a scooter accident already occurred nearby.",
        },
    },
    # roads / high — corrected on this pass from critical. A big pit with
    # water flowing is a real hazard, but nothing here states a crash,
    # a barricade missing, or an arterial road — that's high, not critical.
    # Also the cross-department case: Water Board caused it, Roads fixes it.
    {
        "text": "sadak toot gayi hai kyunki niche ki paani ki pipe leak ho rahi thi, ab bada gadda ban gaya hai aur paani bhi bah raha hai",
        "output": {
            "category": "roads",
            "subcategory": "road_damage_from_leak",
            "priority": "high",
            "confidence": 0.62,
            "location_text": None,
            "summary": "A leaking underground water pipe has damaged the road surface, creating a large pothole with active water flow — likely needs both Water Board and Roads Dept.",
        },
    },
    # roads / high — obstruction blocking a road is high regardless of
    # what's causing it. Also teaches the category-boundary rule: a tree
    # is a ROADS complaint when it's blocking a road, not a PARKS one.
    {
        "text": "Toofan ke baad ek bada ped gir kar poori sadak block kar diya hai, koi bhi gaadi nikal nahi sakti.",
        "output": {
            "category": "roads",
            "subcategory": "fallen_tree_obstruction",
            "priority": "high",
            "confidence": 0.8,
            "location_text": None,
            "summary": "A large tree fell during a storm and is completely blocking the road, preventing any vehicles from passing.",
        },
    },
    # streetlights / medium — a single fixture out, contained. Pairs with
    # the whole-street case below (the scope tie-breaker).
    {
        "text": "Streetlight bahut din se band hai humare gali mein, raat ko andhera rehta hai.",
        "output": {
            "category": "streetlights",
            "subcategory": "light_not_working",
            "priority": "medium",
            "confidence": 0.85,
            "location_text": None,
            "summary": "Streetlight has been non-functional for a while, causing darkness at night.",
        },
    },
    # streetlights / high — same underlying problem as above, but scoped
    # to a whole street for a week: a shared-resource disruption, not a
    # single contained fixture.
    {
        "text": "Poori gali ki saari streetlights ek hafte se band hai, raat ko bilkul andhera rehta hai",
        "output": {
            "category": "streetlights",
            "subcategory": "area_outage",
            "priority": "high",
            "confidence": 0.83,
            "location_text": None,
            "summary": "Every streetlight on the whole street has been off for a week, leaving it completely dark at night.",
        },
    },
    # garbage / medium — contained to one building, real but not
    # widespread.
    {
        "text": "garbage not collected for one week near our apartment, smell is very bad now",
        "output": {
            "category": "garbage",
            "subcategory": "collection_missed",
            "priority": "medium",
            "confidence": 0.75,
            "location_text": None,
            "summary": "Garbage hasn't been collected for a week, causing a bad smell near the apartment.",
        },
    },
    # garbage / high — breeding/disease risk near a shared public space
    # counts as high before any confirmed illness, per the rubric.
    {
        "text": "sabzi mandi ke paas kachra bahut jama ho gaya hai, machariyan bhi ho rahi hai, health issue ho sakta hai",
        "output": {
            "category": "garbage",
            "subcategory": "waste_accumulation",
            "priority": "high",
            "confidence": 0.88,
            "location_text": "sabzi mandi (vegetable market)",
            "summary": "Accumulated garbage near the vegetable market is attracting mosquitoes — a health risk.",
        },
    },
    # garbage / low — specific and located, but trivial. Naming a place
    # doesn't make a complaint serious.
    {
        "text": "Community park ke baahar wale dustbin ka lid tuta hua hai, baaki sab theek hai, overflow nahi ho raha",
        "output": {
            "category": "garbage",
            "subcategory": "bin_maintenance",
            "priority": "low",
            "confidence": 0.7,
            "location_text": "outside the community park",
            "summary": "Dustbin lid near the community park is broken, but the bin itself is not overflowing.",
        },
    },
    # sanitation / medium — a cleaning SERVICE failure, not a waste
    # problem. This is the category's core distinguishing lesson: garbage
    # is about what needs hauling away, sanitation is about whether a
    # service is being performed.
    {
        "text": "community hall ke bahar ka public toilet theek se saaf nahi hota, smell aata rehta hai",
        "output": {
            "category": "sanitation",
            "subcategory": "public_toilet_maintenance",
            "priority": "medium",
            "confidence": 0.58,
            "location_text": "outside the community hall",
            "summary": "Public toilet outside the community hall is not being cleaned regularly.",
        },
    },
    # sanitation / low — vague, no specific street or extent. Sanitation
    # needs its own vague/low anchor rather than borrowing one from
    # another category, given how often it gets confused with garbage.
    {
        "text": "hamare area mein safai kabhi kabhi thik se nahi hoti",
        "output": {
            "category": "sanitation",
            "subcategory": "general_complaint",
            "priority": "low",
            "confidence": 0.35,
            "location_text": None,
            "summary": "Vague complaint about irregular cleanliness with no specific street or extent named.",
        },
    },
    # electricity / critical — actively sparking right now, with people
    # present. Pairs with the unfenced-transformer case below.
    {
        "text": "Electricity pole spark kar raha tha near the bus stand, log dar gaye, bahut dangerous lag raha tha",
        "output": {
            "category": "electricity",
            "subcategory": "sparking_pole",
            "priority": "critical",
            "confidence": 0.92,
            "location_text": "near the bus stand",
            "summary": "A sparking electricity pole near the bus stand alarmed bystanders — immediate safety hazard.",
        },
    },
    # electricity / high — exposed but not (yet) live. This is the exact
    # boundary the critical case above sits on the other side of: a real
    # standing hazard, but not an active one.
    {
        "text": "Transformer ke around fencing nahi hai park ke paas, bachche khelte waqt chhoo sakte hai, abhi tak koi spark nahi hua",
        "output": {
            "category": "electricity",
            "subcategory": "unfenced_equipment",
            "priority": "high",
            "confidence": 0.8,
            "location_text": "near the park",
            "summary": "A transformer near the park has no protective fencing and children playing nearby could touch it; no sparking has occurred yet.",
        },
    },
    # drainage / critical — an actual uncovered hole someone could fall
    # into. The cleanest possible anchor for the critical fall-in test.
    {
        "text": "There is an open manhole right outside City Hospital's main gate, very dangerous at night, someone could fall in.",
        "output": {
            "category": "drainage",
            "subcategory": "open_manhole",
            "priority": "critical",
            "confidence": 0.93,
            "location_text": "City Hospital main gate",
            "summary": "Open, unmarked manhole outside City Hospital's main gate poses an immediate safety risk.",
        },
    },
    # drainage / high — sunken but still covered: a vehicle/trip hazard,
    # not a fall-in hazard. Direct contrast with the open-manhole case.
    {
        "text": "Manhole ka dhakkan sadak se thoda neeche dhab gaya hai, gaadiyon ko jhatka lagta hai lekin manhole khula nahi hai",
        "output": {
            "category": "drainage",
            "subcategory": "sunken_frame",
            "priority": "high",
            "confidence": 0.8,
            "location_text": None,
            "summary": "A manhole cover has sunk slightly below road level, jolting vehicles, but it is still covered, not open.",
        },
    },
    # parks / medium — deliberately NOT high or critical: this hazard
    # needs someone to actively use the broken equipment to cause harm,
    # unlike an ambient hazard (a leaning pole, a cracking branch) that
    # threatens anyone nearby regardless of interaction.
    {
        "text": "park ka swing tuta hua hai bahut time se, bachche gir sakte hai",
        "output": {
            "category": "parks",
            "subcategory": "damaged_equipment",
            "priority": "medium",
            "confidence": 0.6,
            "location_text": None,
            "summary": "A broken swing in the park has been unrepaired for a while, risk to children if used.",
        },
    },
    # parks / low — cosmetic wear on a fixture that still works fine.
    {
        "text": "Park ke gate par purani paint ukhad rahi hai, gate waise theek se khulta aur band hota hai",
        "output": {
            "category": "parks",
            "subcategory": "cosmetic_wear",
            "priority": "low",
            "confidence": 0.7,
            "location_text": None,
            "summary": "Paint is peeling off the park gate, but the gate itself still opens and closes fine.",
        },
    },
    # other / low — genuinely vague, no specific problem, place, or
    # person. The generic vague-complaint-is-low anchor for the set.
    {
        "text": "not happy with the service overall, things could be better",
        "output": {
            "category": "other",
            "subcategory": "general_feedback",
            "priority": "low",
            "confidence": 0.3,
            "location_text": None,
            "summary": "Vague general feedback with no specific civic issue described.",
        },
    },
    # other / critical — the catch-all category can still be critical.
    # A structure actively about to collapse onto the public is critical
    # regardless of it being privately owned; the danger is to the public,
    # and no single department among the 9 clearly owns a private
    # building's structural failure.
    {
        "text": "Purani building ki compound wall crack ho kar jhukna shuru ho gayi hai school ke bahar, kabhi bhi gir sakti hai bachchon par",
        "output": {
            "category": "other",
            "subcategory": "structural_hazard",
            "priority": "critical",
            "confidence": 0.85,
            "location_text": "outside the school",
            "summary": "An old building's compound wall has cracked and started leaning outside a school, and could collapse onto children at any moment.",
        },
    },
]
