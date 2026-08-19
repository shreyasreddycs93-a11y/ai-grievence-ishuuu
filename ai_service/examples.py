# -*- coding: utf-8 -*-
"""
Few-shot examples used inside the classification prompt (see prompts.py).
These are baked into every classify_complaint() call so the model has
solved examples to pattern-match against, instead of classifying cold.

Generated from docs/CLASSIFICATION_DESIGN.md via a rule-coverage matrix:
every rule in the design spec's §1 (category boundary rulings) and §2
(priority escalation rules and tie-breaker) maps to at least one example
below. Passed a 12-point audit before being committed here.

The 0.5-0.7 confidence band is a DELIBERATE design requirement, not an
accident of these particular cases — spec §3 requires mid-confidence
examples to be present from the start so the model has a pattern for "I
answered but I'm not fully sure," instead of only ever seeing confident
anchors. There are exactly 6 examples in that band. Do not remove or
"round up" any of them during future edits — losing that band collapses
confidence calibration back toward always-high, which is the failure mode
this design requirement exists to prevent.

This file assumes/declares UTF-8 source encoding (Python 3's default) so
the native-script text below (Kannada, Tamil, Telugu, Hindi, Bengali,
Marathi) is preserved byte-for-byte. Do not let an editor silently
re-encode this file.

Keep this list realistic and varied. If you or your teammate refine these
with Gemini/ChatGPT, replace the whole list — don't hand-edit piecemeal,
since the prompt is tuned against the set as a whole and the coverage/
tally requirements (category and priority distribution, the confidence
band) hold for the set, not for any single entry.
"""

FEW_SHOT_EXAMPLES = [
    {
        "text": "Humari gali me ek bada gaddha ho gaya hai 4th cross ke paas, scooter walo ko dikkat hoti hai raat me",
        "output": {
            "reasoning": "Residential-lane pothole with no stated accident or arterial road stays medium; roads owns the resurfacing.",
            "category": "roads",
            "subcategory": "pothole",
            "priority": "medium",
            "confidence": 0.85,
            "location_text": "near 4th cross",
            "summary": "Large pothole near 4th cross troubling two-wheelers at night.",
        },
    },
    {
        "text": "ABSOLUTELY FED UP!!! This corporation is USELESS — that fellow has set up his pani puri cart AGAIN on our corner without any licence. SHAME ON YOU ALL, is anyone even working there???",
        "output": {
            "reasoning": "Anger and capitals carry no priority weight; unlicensed vending is an enforcement matter (other) and poses no danger, so low.",
            "category": "other",
            "subcategory": "unlicensed_vending",
            "priority": "low",
            "confidence": 0.82,
            "location_text": "our corner",
            "summary": "Unlicensed food cart repeatedly set up at a street corner.",
        },
    },
    {
        "text": "ಶಾಲೆ ಹತ್ತಿರ ಕರೆಂಟ್ ಕಂಬದಿಂದ ವೈರ್ ಕಿತ್ತು ಜೋತಾಡ್ತಿದೆ, ಸ್ಪಾರ್ಕ್ ಬರ್ತಿದೆ, ಮಕ್ಕಳು ಓಡಾಡೋ ಜಾಗ, ಬೇಗ ಬನ್ನಿ",
        "output": {
            "reasoning": "A sparking detached live wire where children walk is an immediate electrocution risk — the physical-harm test for critical is met.",
            "category": "electricity",
            "subcategory": "live_wire_hazard",
            "priority": "critical",
            "confidence": 0.92,
            "location_text": "near the school",
            "summary": "Sparking live wire hanging from a pole beside a school.",
        },
    },
    {
        "text": "Ek kutta mar gaya hai road side pe school wali gali me, 3 din ho gaye koi uthane nahi aaya, ab bahut badbu aa rahi hai aur bachhe wahi se jaate hain",
        "output": {
            "reasoning": "A carcass is a haulage job (garbage, not sanitation), and three days unaddressed escalates it one level to high.",
            "category": "garbage",
            "subcategory": "dead_animal_removal",
            "priority": "high",
            "confidence": 0.65,
            "location_text": "school lane",
            "summary": "Dog carcass uncollected for 3 days on a lane used by schoolchildren.",
        },
    },
    {
        "text": "There is a steady leak from the joint of the water pipe outside house 23, Rose Garden Layout since this morning. Clean water is getting wasted onto the street.",
        "output": {
            "reasoning": "A fresh, contained leak with wastage but no injury path or supply loss sits at medium; water_supply owns the pipe repair.",
            "category": "water_supply",
            "subcategory": "pipe_leak",
            "priority": "medium",
            "confidence": 0.84,
            "location_text": "house 23, Rose Garden Layout",
            "summary": "Pipe joint leaking clean water onto the street since morning.",
        },
    },
    {
        "text": "எங்க ஏரியா பஸ் ஸ்டாப் பக்கத்து பொது கழிப்பறை ரொம்ப அசுத்தமா இருக்கு, இன்னைக்கு காலையில பார்த்தேன், சுத்தம் பண்ண ஆள் வரலை போல",
        "output": {
            "reasoning": "A cleaning service not being performed is sanitation, and a freshly noticed dirty facility with no stated health impact is medium.",
            "category": "sanitation",
            "subcategory": "public_toilet_cleaning",
            "priority": "medium",
            "confidence": 0.80,
            "location_text": "public toilet near the bus stop",
            "summary": "Public toilet near bus stop found uncleaned this morning.",
        },
    },
    {
        "text": "The benches near the east gate of Jayanagar Mini Park have peeling paint and the hedge border has grown untidy. Please schedule maintenance.",
        "output": {
            "reasoning": "Cosmetic upkeep of park assets is low — the exact location makes this specific, not serious.",
            "category": "parks",
            "subcategory": "routine_maintenance",
            "priority": "low",
            "confidence": 0.86,
            "location_text": "east gate, Jayanagar Mini Park",
            "summary": "Park benches need repainting and hedges need trimming at Jayanagar Mini Park.",
        },
    },
    {
        "text": "Main market road pe 10-12 cattle beech sadak pe baithe rehte hai, gaadiya miss ho rahi hai, kal ek bike wala girte girte bacha, aur waha divider ka tukda bhi toota pada hai",
        "output": {
            "reasoning": "Animals physically obstructing a main road fall under roads (obstruction rule, not animal-control 'other'), a blocked shared road with a near-miss is high, and the broken divider is secondary — multi-issue caps confidence.",
            "category": "roads",
            "subcategory": "road_obstruction",
            "priority": "high",
            "confidence": 0.60,
            "location_text": "main market road",
            "summary": "Cattle blocking main market road causing near-accidents; divider also broken.",
        },
    },
    {
        "text": "Some stray dogs have started sitting near the lane entrance in the evenings. Nothing has happened but elderly walkers are a bit nervous.",
        "output": {
            "reasoning": "Animal control has no engineering owner so this is other; low vs medium were both defensible and the tie-break rule resolves down to low, capping confidence.",
            "category": "other",
            "subcategory": "stray_animals",
            "priority": "low",
            "confidence": 0.55,
            "location_text": "lane entrance",
            "summary": "Stray dogs gathering at lane entrance in evenings; no incident reported.",
        },
    },
    {
        "text": "మా వీధిలో పైపు లీక్ అయ్యి రోడ్డు మధ్యలో గుంత పడింది, నీళ్ళు ఆగిపోయాయి కానీ రోడ్డు అలాగే ఉంది, బండ్లు జారుతున్నాయి",
        "output": {
            "reasoning": "The pipe caused it but the complaint needs the road fixed, so roads owns the fix — category was weighed against water_supply, capping confidence; contained residential damage is medium.",
            "category": "roads",
            "subcategory": "road_damage_from_leak",
            "priority": "medium",
            "confidence": 0.58,
            "location_text": "our street",
            "summary": "Road sunken where a pipe leaked; leak stopped but vehicles are slipping.",
        },
    },
    {
        "text": "KYA BAKWAS DEPARTMENT HAI!!! pole no 18 ki light kal se flicker maar rahi hai, ON OFF ON OFF, dimag kharab ho gaya hai pura!!!",
        "output": {
            "reasoning": "A single flickering pole light is trivial regardless of the furious tone — anger carries no priority weight.",
            "category": "streetlights",
            "subcategory": "flickering_light",
            "priority": "low",
            "confidence": 0.80,
            "location_text": "pole no. 18",
            "summary": "Streetlight at pole 18 flickering since yesterday.",
        },
    },
    {
        "text": "Storm drain on our street has burst and black water is flowing straight into the ground floor rooms of two houses right now, people are moving children out.",
        "output": {
            "reasoning": "Floodwater actively entering occupied homes meets the critical physical-harm test — this is happening now, not a future risk.",
            "category": "drainage",
            "subcategory": "sewage_flooding_homes",
            "priority": "critical",
            "confidence": 0.90,
            "location_text": "our street",
            "summary": "Burst storm drain flooding sewage into two occupied ground-floor homes.",
        },
    },
    {
        "text": "हमारे पूरे वार्ड में कल रात से बिजली नहीं है, ट्रांसफार्मर से आवाज़ आई थी उसके बाद से सब बंद है, पूरा मोहल्ला परेशान है",
        "output": {
            "reasoning": "A whole-ward outage is a shared-resource disruption affecting many people at once, which is high on its own.",
            "category": "electricity",
            "subcategory": "area_power_outage",
            "priority": "high",
            "confidence": 0.85,
            "location_text": "entire ward",
            "summary": "Ward-wide power outage since last night after a transformer noise.",
        },
    },
    {
        "text": "The lid of the community bin at the corner of 5th Main is cracked and won't close fully. Bin itself is emptied on time.",
        "output": {
            "reasoning": "A cracked bin lid with collection running normally is cosmetic — a precise location makes it specific, not serious.",
            "category": "garbage",
            "subcategory": "damaged_bin",
            "priority": "low",
            "confidence": 0.84,
            "location_text": "corner of 5th Main",
            "summary": "Community bin lid cracked at 5th Main; collection unaffected.",
        },
    },
    {
        "text": "Subzi mandi ke paas wala public toilet ek hafte se saaf nahi hua, andar jaana impossible hai, aas paas ke dukan wale sab pareshan, machhar bhi ho gaye hai waha",
        "output": {
            "reasoning": "A cleaning service unperformed for a week at a high-footfall market with mosquito breeding is a shared-facility disruption plus disease risk — high.",
            "category": "sanitation",
            "subcategory": "public_toilet_neglect",
            "priority": "high",
            "confidence": 0.82,
            "location_text": "public toilet near the vegetable market",
            "summary": "Market public toilet uncleaned for a week; unusable and breeding mosquitoes.",
        },
    },
    {
        "text": "Corner wali nali kachre se block ho gayi hai, thoda pani road pe jama hota hai shaam ko, badbu bhi hai",
        "output": {
            "reasoning": "A choked drain with limited evening pooling and no flooding or breeding stated was weighed high vs medium — tie-break lands on the lower, and the weighing caps confidence.",
            "category": "drainage",
            "subcategory": "blocked_drain",
            "priority": "medium",
            "confidence": 0.55,
            "location_text": "corner drain",
            "summary": "Corner drain blocked; some smelly water pools on the road by evening.",
        },
    },
    {
        "text": "পাশের বাড়ির বাগানের বোগেনভিলিয়া ডালপালা আমাদের দেওয়ালের উপর দিয়ে ঝুলে রাস্তায় চলে এসেছে, ফুল পাতা পড়ে গেট নোংরা হয়ে যায়",
        "output": {
            "reasoning": "Vegetation from a private garden is not a parks asset — this is a private-property nuisance (other), and a messy gate is cosmetic, so low.",
            "category": "other",
            "subcategory": "private_vegetation_nuisance",
            "priority": "low",
            "confidence": 0.80,
            "location_text": "neighbour's wall by our gate",
            "summary": "Neighbour's bougainvillea overhanging the wall, littering the gate area.",
        },
    },
    {
        "text": "Nehru park ka jhula ek chain se latak raha hai, seat tedhi ho gayi hai, bachhe phir bhi jhool rahe hai uspe",
        "output": {
            "reasoning": "Damaged park equipment that is unsafe to use but not an imminent serious-injury scenario degrades the facility — medium, owned by parks.",
            "category": "parks",
            "subcategory": "broken_play_equipment",
            "priority": "medium",
            "confidence": 0.80,
            "location_text": "Nehru park",
            "summary": "Swing at Nehru park hanging by one chain while children still use it.",
        },
    },
    {
        "text": "मेन लाईन फुटली आहे, पाणी इतक्या जोरात उडतंय की काल एक आजी तिथे पडल्या, रस्त्यावर उभं राहणं पण अवघड झालंय, लवकर या",
        "output": {
            "reasoning": "A pressurized burst forceful enough that a person has already fallen meets the critical physical-harm test — injury has occurred and remains likely.",
            "category": "water_supply",
            "subcategory": "pressurized_main_burst",
            "priority": "critical",
            "confidence": 0.87,
            "location_text": None,
            "summary": "Forceful water-main burst; an elderly woman already fell, area hard to stand in.",
        },
    },
    {
        "text": "Humari puri gali ki saari lights 4 din se band hai, roz complaint karte hai koi nahi aata, raat ko bilkul andhera rehta hai",
        "output": {
            "reasoning": "A whole-lane outage weighed medium vs high, but four days of explicit neglect fires the duration escalation, which resolves the tie upward — the weighing still caps confidence.",
            "category": "streetlights",
            "subcategory": "street_wide_outage",
            "priority": "high",
            "confidence": 0.58,
            "location_text": "our lane",
            "summary": "All streetlights in the lane dead for 4 days despite daily complaints.",
        },
    },
]
