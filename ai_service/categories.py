"""
The ONLY allowed values for category and priority — this is the single
source of truth referenced in the Team Integration Guide's "Locked Decisions".
classify_complaint() validates its output against these lists before
returning anything to the backend. If the model returns something outside
these lists, it gets mapped to a safe default, never passed through.
"""

CATEGORIES = [
    "water_supply",
    "roads",
    "sanitation",
    "electricity",
    "streetlights",
    "drainage",
    "garbage",
    "parks",
    "other",
]

PRIORITIES = ["low", "medium", "high", "critical"]

DEFAULT_CATEGORY = "other"
DEFAULT_PRIORITY = "medium"

# Phase 3 (split_departments): the most department entries one complaint may
# be split into. Lives here rather than in service.py because BOTH the
# prompt (which tells the model the ceiling) and the validator (which
# enforces it) need it, and service.py imports prompts.py — so a constant
# defined in service.py could not be read by prompts.py without a circular
# import. See docs/SPLIT_DEPARTMENTS_DESIGN.md §1 rule 3.
MAX_DEPARTMENTS = 4

# Confidence below this means the backend should flag needs_human_review=true.
# (Enforcement of that flag happens in the backend, not here — this constant
# is just kept in sync for reference.)
HUMAN_REVIEW_CONFIDENCE_THRESHOLD = 0.6
