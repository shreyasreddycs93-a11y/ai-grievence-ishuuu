"""
Few-shot examples for build_split_departments_prompt() (Phase 3).

Independently authored from ai_service/tests/split_holdout_set.py — NO text
here may overlap with a holdout case, or the holdout score becomes
meaningless the moment the model has seen the answer. See that module's
docstring and docs/SPLIT_DEPARTMENTS_DESIGN.md Section 3's no-overlap audit
item.

Model-facing output schema only: "output" contains "reasoning" and
"departments" — never is_split/source/fallback, since those are computed by
service.py's _validate_split_departments() and never predicted by the model.
Each department item DOES include confidence/excerpt/location_text here
(unlike the holdout set's ground truth), because those ARE things the model
is asked to produce on every real call.
"""

SPLIT_FEW_SHOT_EXAMPLES = [

    # 1. No-split baseline
    {
        "text": "The public tap at the corner of 4th Cross has been leaking continuously since this morning, water is pooling on the ground.",
        "output": {
            "reasoning": "Single issue, freshly reported and still containable, so one department at the lower of two plausible levels.",
            "departments": [
                {
                    "category": "water_supply", "subcategory": "leaking_tap", "priority": "medium",
                    "confidence": 0.88, "excerpt": "leaking continuously since this morning",
                    "location_text": "corner of 4th Cross",
                },
            ],
        },
    },

    # 2. Causation trap — ACTIVE leak, one department (cause owner)
    {
        "text": "A big water pipe burst under the road near the bus stand two hours ago and is still gushing, part of the tar road has already caved in where the water is pooling.",
        "output": {
            "reasoning": "The caved road section is downstream damage from a leak that is still actively running — roads cannot fix anything until the water is shut off, so this is one dispatch to the cause owner, not two.",
            "departments": [
                {
                    "category": "water_supply", "subcategory": "burst_pipe", "priority": "high",
                    "confidence": 0.8, "excerpt": "burst under the road...still gushing...caved in",
                    "location_text": "near the bus stand",
                },
            ],
        },
    },

    # 3. Causation, leak already RESOLVED — one department (fix owner), contrast to #2
    {
        "text": "Three weeks ago a water pipe leak damaged the road on 9th Cross. The leak was fixed by the water department last week, but the resulting pothole is still there and getting worse.",
        "output": {
            "reasoning": "The leak itself is already stopped (fixed last week) — nothing remains for water_supply to do, so the still-open pothole is now a plain roads resurfacing job. Contrast with an active leak, which stays with the cause owner until it stops.",
            "departments": [
                {
                    "category": "roads", "subcategory": "pothole", "priority": "medium",
                    "confidence": 0.78, "excerpt": "resulting pothole is still there and getting worse",
                    "location_text": "9th Cross",
                },
            ],
        },
    },

    # 4. Symptom trap — one department
    {
        "text": "Our street's drain is completely choked and dirty water has spread across half the road, flies are gathering.",
        "output": {
            "reasoning": "The spread water and flies are both downstream symptoms of the same choked drain — clearing the drain fixes all of it, one crew.",
            "departments": [
                {
                    "category": "drainage", "subcategory": "blocked_drain", "priority": "high",
                    "confidence": 0.83, "excerpt": "completely choked and dirty water has spread...flies are gathering",
                    "location_text": "our street",
                },
            ],
        },
    },

    # 5. Obvious 2-way, wide priority gap
    {
        "text": "A transformer near the school gate sparks badly and looks like it could catch fire at any moment. Separately, the road divider paint markings near the same junction have faded and are barely visible now.",
        "output": {
            "reasoning": "Two unconnected issues at the same junction: a sparking transformer is an immediate fire/shock risk (critical), while faded paint is cosmetic with nobody in danger (low). Priority is judged per item, not averaged.",
            "departments": [
                {
                    "category": "electricity", "subcategory": "transformer_hazard", "priority": "critical",
                    "confidence": 0.93, "excerpt": "sparks badly and looks like it could catch fire",
                    "location_text": "near the school gate",
                },
                {
                    "category": "roads", "subcategory": "faded_markings", "priority": "low",
                    "confidence": 0.7, "excerpt": "divider paint markings...faded and are barely visible",
                    "location_text": "same junction",
                },
            ],
        },
    },

    # 6. Obvious 2-way, different category-boundary reasoning per item
    {
        "text": "The public toilet near the market has not been cleaned in over a week and smells very bad. Also, the collection bin two streets away has been overflowing for four days, rats have started gathering around it and shopkeepers say customers are turning away because of the smell.",
        "output": {
            "reasoning": "A cleaning-service backlog (sanitation) with no new consequence stays at its base level regardless of duration, while the overflowing bin has escalated with a stated vector/disease risk (rats), which is sufficient for high on its own even before any confirmed illness.",
            "departments": [
                {
                    "category": "sanitation", "subcategory": "uncleaned_facility", "priority": "medium",
                    "confidence": 0.75, "excerpt": "not been cleaned in over a week and smells very bad",
                    "location_text": "public toilet near the market",
                },
                {
                    "category": "garbage", "subcategory": "overflow", "priority": "high",
                    "confidence": 0.82, "excerpt": "overflowing for four days, rats have started gathering",
                    "location_text": "collection bin two streets away",
                },
            ],
        },
    },

    # 7. 3-way, all high but for different reasons
    {
        "text": "Since last night's heavy rain, a stormwater drain near the crossing has overflowed and sewage is flowing onto the road, one of the roadside electric poles is leaning at an angle after the ground eroded around its base, and there is a large pothole further down the same road where two scooters skidded and fell this morning.",
        "output": {
            "reasoning": "Three unrelated physical fixes despite one storm as the common trigger: sewage overflow is a disease-risk shared-resource disruption, a leaning-but-not-yet-fallen pole is a would-become-critical-if-ignored hazard, and a pothole with a stated accident is escalated one level above an ordinary pothole.",
            "departments": [
                {
                    "category": "drainage", "subcategory": "sewage_overflow", "priority": "high",
                    "confidence": 0.85, "excerpt": "overflowed and sewage is flowing onto the road",
                    "location_text": "near the crossing",
                },
                {
                    "category": "electricity", "subcategory": "leaning_pole", "priority": "high",
                    "confidence": 0.72, "excerpt": "leaning at an angle after the ground eroded around its base",
                    "location_text": "roadside, same crossing",
                },
                {
                    "category": "roads", "subcategory": "pothole", "priority": "high",
                    "confidence": 0.87, "excerpt": "two scooters skidded and fell this morning",
                    "location_text": "further down the same road",
                },
            ],
        },
    },

    # 8. Max-limit, 5 issues named -> cap at 4, drop the cosmetic one
    {
        "text": "After the storm our lane has many problems - a live wire is hanging and sparking over the footpath, the main road has a deep pothole where a scooter fell, the drain is completely blocked and vehicles cannot pass through the standing water, the streetlight at the corner has been off for two weeks, and the small nameplate sign for our lane has fallen down and is lying on the ground.",
        "output": {
            "reasoning": "Five distinct issues are named but only 4 departments may be returned. The fallen lane nameplate is the only one endangering nobody and blocking nothing, so it is dropped; the other four are kept even though they are not all the same priority.",
            "departments": [
                {
                    "category": "electricity", "subcategory": "live_wire_hazard", "priority": "critical",
                    "confidence": 0.94, "excerpt": "live wire is hanging and sparking over the footpath",
                    "location_text": "our lane",
                },
                {
                    "category": "roads", "subcategory": "pothole", "priority": "high",
                    "confidence": 0.86, "excerpt": "deep pothole where a scooter fell",
                    "location_text": "main road",
                },
                {
                    "category": "drainage", "subcategory": "blocked_drain", "priority": "high",
                    "confidence": 0.8, "excerpt": "completely blocked and vehicles cannot pass through the standing water",
                    "location_text": "our lane",
                },
                {
                    "category": "streetlights", "subcategory": "single_lamp_out", "priority": "medium",
                    "confidence": 0.7, "excerpt": "streetlight at the corner has been off for two weeks",
                    "location_text": "corner of our lane",
                },
            ],
        },
    },

    # 9. Same root cause, two genuinely different locations/effects -> still splits
    {
        "text": "A herd of stray cattle has been sitting in the middle of the main road for two days causing vehicles to swerve dangerously, and separately there have been reports of the same animals damaging the fencing around the community garden at night.",
        "output": {
            "reasoning": "One root cause (the cattle) but two unrelated physical fixes in two different places: cattle physically obstructing the road falls under the general obstruction rule (roads), while fence damage at the garden is a parks asset repair — shared causation alone is not a reason to merge when the effects and locations are distinct, unlike a symptom trap where everything is downstream at one spot.",
            "departments": [
                {
                    "category": "roads", "subcategory": "animal_obstruction", "priority": "high",
                    "confidence": 0.77, "excerpt": "sitting in the middle of the main road...vehicles to swerve dangerously",
                    "location_text": "main road",
                },
                {
                    "category": "parks", "subcategory": "fence_damage", "priority": "medium",
                    "confidence": 0.68, "excerpt": "damaging the fencing around the community garden",
                    "location_text": "community garden",
                },
            ],
        },
    },

    # 10. No-split baseline, contrast to #9: single cause, single location, duration escalation
    {
        "text": "Overflowing water from a broken tap outside the community hall has been flooding the small courtyard in front of it for two days, making the entrance slippery.",
        "output": {
            "reasoning": "Single cause, single effect, single location — nothing to split. A contained leak explicitly unaddressed for two days moves up one level from its fresh-report baseline.",
            "departments": [
                {
                    "category": "water_supply", "subcategory": "broken_tap", "priority": "high",
                    "confidence": 0.81, "excerpt": "flooding the small courtyard...for two days",
                    "location_text": "outside the community hall",
                },
            ],
        },
    },
]
