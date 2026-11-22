"""
HELD-OUT TEST SET for split_departments() -- 25 blind-labeled complaints.

Ground truth for Phase 3 department splitting. Same hard rule as
holdout_set.py: NOTHING in this file may ever be copied into the few-shot
example set for build_split_departments_prompt(). The moment a case appears
in the prompt it stops being a valid held-out test and the score becomes
meaningless.

When the model disagrees with a label here, investigate the label first --
these labels encode the splitting rubric in docs/SPLIT_DEPARTMENTS_DESIGN.md
Section 2, and a mismatch is evidence about that rubric's coverage, not
automatically a model error.

Fields per case:
    text                  -- the complaint, native script preserved as-is
    expected_departments  -- ordered list of {"category", "priority"} dicts.
                             EXACTLY ONE item for a no-split case -- never an
                             empty list, and never a separate expected_is_split
                             field: the scorer derives is_split from
                             len(expected_departments) > 1, the same way
                             _validate_split_departments() derives it in
                             service.py. Order is not significant; the scorer
                             must compare as a set.
    note                  -- why this label, in the labeler's own words. For
                             trap cases this states explicitly why the
                             secondary issue does NOT get its own entry.
    lang                  -- language/script tag (en, hinglish, hi, kn, ta,
                             te, bn, mr)
    tags                  -- free-form (no_split, causation_trap,
                             symptom_trap, obvious_split, priority_independent,
                             confidence_variance, max_limit)
    borderline            -- present + True when two labelings are defensible
    borderline_note       -- explains the alternate reading, when borderline
    also_accept_departments -- alternate acceptable department list, if any

DELIBERATELY NOT LABELED HERE: confidence, excerpt, location_text.
Confidence is the model's own self-assessment, not a labelable fact.
Excerpt/location extraction is real behavior but too string-fragile to score
by exact match -- both are audited by inspecting live output, per the design
doc's R3/R4/R9 "runtime audit only" marking. The scorer checks department
count and per-department category/priority only.

OPEN RULING (slots 4-6, causation traps): docs/SPLIT_DEPARTMENTS_DESIGN.md's
R7 says a burst pipe washing out a road routes to water_supply (the
underlying-cause owner), while docs/CLASSIFICATION_DESIGN.md line 45 says a
road damaged by a leaking pipe is roads (the physical-fix owner). These
labels reconcile the two by leak state: while the leak is ACTIVE the fix is
water_supply's (the road cannot be repaired until the water stops), and once
the leak is stopped the remaining damaged road is roads'. All three causation
traps below are active-leak cases. This reconciliation needs ratifying into
one of the two design docs before these labels are treated as settled.
"""

SPLIT_HOLDOUT_SET = [

    # ---------------------------------------------------------------
    # Slots 1-3 -- no split, baseline single-issue
    # ---------------------------------------------------------------

    # 1. Hinglish - single pothole, no second issue
    {
        'text': 'Hamari gali me 2nd cross ke paas bada gaddha ban gaya hai, barish ke baad aur gehra ho gaya hai, scooter wale girte girte bache hain',
        'expected_departments': [
            {'category': 'roads', 'priority': 'medium'},
        ],
        'note': 'Single issue, nothing to split. Deliberately a residential lane ("hamari gali"), NOT a named arterial road -- an arterial road is itself a high trigger, which would make this baseline slot ambiguous. Near-misses only ("girte girte bache"): no accident has actually happened, so the harm-already-occurred escalation does not fire and an ordinary side-road pothole stays medium.',
        'lang': 'hinglish',
        'tags': ['no_split'],
    },

    # 2. Tamil - whole-street water outage, single issue
    {
        'text': 'எங்கள் தெருவில் கடந்த மூன்று நாட்களாக குடிநீர் வரவே இல்லை, டேங்கர் லாரி அனுப்புவதாக சொன்னார்கள் ஆனால் இன்னும் வரவில்லை',
        'expected_departments': [
            {'category': 'water_supply', 'priority': 'high'},
        ],
        'note': 'Single issue. Whole-street supply completely out for three days with the promised tanker never arriving -- a whole-area outage, so high. The unmet tanker promise is part of the same complaint, not a second department.',
        'lang': 'ta',
        'tags': ['no_split'],
    },

    # 3. English - ONE streetlight out (contrast to whole-street outage)
    {
        'text': 'The streetlight in front of house number 42, 5th Main, Jayanagar stopped working two nights ago. The rest of the lights on the lane are working fine.',
        'expected_departments': [
            {'category': 'streetlights', 'priority': 'medium'},
        ],
        'note': 'Single issue. Deliberately contrasts case 2 and the whole-lane outages later in this set: ONE lamp out with the rest of the lane lit is not an area outage, so it stays medium. Kept deliberately RECENT ("two nights ago") so the multi-day-duration escalation does not fire -- a ten-day version of this same complaint would escalate a level and stop being a clean baseline.',
        'lang': 'en',
        'tags': ['no_split'],
    },

    # ---------------------------------------------------------------
    # Slots 4-6 -- no split, CAUSATION trap (pipe damaging road)
    # ---------------------------------------------------------------

    # 4. English - burst pipe actively washing away road
    {
        'text': 'A water pipeline has burst near the corner of 7th Cross and has been gushing continuously since yesterday evening. The water is running down the lane and has already washed away a section of the mud road.',
        'expected_departments': [
            {'category': 'water_supply', 'priority': 'high'},
        ],
        'note': 'CAUSATION TRAP. The washed-away road is tempting as a second roads entry, but it is downstream damage from a leak that is still running -- roads cannot resurface anything until the water is shut off, so this is one dispatch, not two. High because a burst main left unaddressed overnight is already causing structural damage.',
        'lang': 'en',
        'tags': ['no_split', 'causation_trap'],
    },

    # 5. Kannada - two-day pipe leak, asphalt lifting
    {
        'text': 'ನಮ್ಮ ಬಡಾವಣೆಯಲ್ಲಿ ಮುಖ್ಯ ನೀರಿನ ಪೈಪ್ ಒಡೆದು ಎರಡು ದಿನಗಳಿಂದ ನೀರು ಸೋರುತ್ತಿದೆ, ರಸ್ತೆ ಎಲ್ಲಾ ಕೆಸರಾಗಿದೆ ಮತ್ತು ಡಾಂಬರು ಕಿತ್ತು ಬರುತ್ತಿದೆ',
        'expected_departments': [
            {'category': 'water_supply', 'priority': 'high'},
        ],
        'note': 'CAUSATION TRAP. Lifting asphalt and mud are symptoms of the live leak, not a separate roads job yet. Two days explicitly unaddressed puts this at high per the leak-duration rule.',
        'lang': 'kn',
        'tags': ['no_split', 'causation_trap'],
    },

    # 6. Hindi - three-day leak, road has sunk
    {
        'text': 'हमारी गली में पानी की लाइन में लीकेज है, तीन दिन से लगातार रिस रहा है, अब सड़क धंस गई है और वहाँ गड्ढा बन गया है',
        'expected_departments': [
            {'category': 'water_supply', 'priority': 'high'},
        ],
        'note': 'CAUSATION TRAP, hardest of the three: the road has actually subsided, which reads like a roads complaint. Still one department -- the subsidence will continue until the leak is stopped, so water_supply owns the fix. High on three days unaddressed.',
        'lang': 'hi',
        'tags': ['no_split', 'causation_trap'],
        'borderline': True,
        'borderline_note': 'Defensible as a 2-way split (water_supply + roads) once the leak is stopped and the sunken road still needs resurfacing -- but at the time of complaint the leak is still active, so a single water_supply dispatch is correct. See the OPEN RULING in this module docstring.',
    },

    # ---------------------------------------------------------------
    # Slots 7-9 -- no split, SYMPTOM trap (blocked drain making a mess)
    # ---------------------------------------------------------------

    # 7. Telugu - blocked drain, sewage on road, mosquitoes
    {
        'text': 'మా వీధిలో మురుగు కాలువ పూర్తిగా మూసుకుపోయి మురుగునీరు రోడ్డు మీద పారుతోంది, చాలా దుర్వాసన వస్తోంది, దోమలు కూడా విపరీతంగా పెరుగుతున్నాయి',
        'expected_departments': [
            {'category': 'drainage', 'priority': 'high'},
        ],
        'note': 'SYMPTOM TRAP. Sewage on the road looks like a sanitation job and the mosquitoes look like a separate health issue, but both disappear the moment the drain is unblocked -- one root fix, one department. High because mosquito breeding counts as a disease risk before any confirmed illness.',
        'lang': 'te',
        'tags': ['no_split', 'symptom_trap'],
    },

    # 8. Hindi - contained drain blockage, smell starting
    {
        'text': 'नाली जाम है और गंदा पानी धीरे-धीरे रिसकर गली के किनारे जमा हो रहा है, अभी ज्यादा नहीं फैला है लेकिन बदबू शुरू हो गई है',
        'expected_departments': [
            {'category': 'drainage', 'priority': 'medium'},
        ],
        'note': 'SYMPTOM TRAP with a deliberately lower priority than case 7, so the trap set is not all-high. Still contained, nothing spread across the road, no breeding stated -- medium. The smell is a symptom of the blockage, not a sanitation dispatch.',
        'lang': 'hi',
        'tags': ['no_split', 'symptom_trap'],
    },

    # 9. Telugu - garbage IS the blockage
    {
        'text': 'కాలువలో చెత్త అంతా పేరుకుపోయి నీరు అస్సలు పోవడం లేదు, వర్షం వస్తే వీధి అంతా నీళ్ళు నిలుస్తున్నాయి',
        'expected_departments': [
            {'category': 'drainage', 'priority': 'medium'},
        ],
        'note': 'SYMPTOM TRAP, sharpest form: garbage is literally named in the text, which strongly baits a second garbage entry. But the garbage is INSIDE the drain -- clearing it IS the drain-clearing operation, one crew, one dispatch. Medium because the flooding is conditional on rain rather than currently blocking the street.',
        'lang': 'te',
        'tags': ['no_split', 'symptom_trap'],
    },

    # ---------------------------------------------------------------
    # Slots 10-13 -- 2-way split, INDEPENDENT PRIORITY
    # ---------------------------------------------------------------

    # 10. English - critical live wire + low broken benches
    {
        'text': 'There is a live electrical wire hanging low near the transformer at the park entrance on 3rd Main and it sparks whenever there is any wind. Children play right underneath it. Also the benches inside the park have been broken for months and nobody has come to repair them.',
        'expected_departments': [
            {'category': 'electricity', 'priority': 'critical'},
            {'category': 'parks', 'priority': 'low'},
        ],
        'note': 'Widest priority gap in the set. Sparking live wire above playing children meets the immediate-physical-harm test for critical; broken benches are a months-old amenity defect with nobody in danger, so low. A model that averages these to two mediums has failed the independence rule.',
        'lang': 'en',
        'tags': ['obvious_split', 'priority_independent'],
    },

    # 11. Bengali - high garbage + low signage
    {
        'text': 'আমাদের পাড়ার ভ্যাটে গত এক সপ্তাহ ধরে আবর্জনা উপচে পড়ছে, দুর্গন্ধে টেকা যাচ্ছে না আর মশা বাড়ছে। এছাড়া পার্কের গেটের সাইনবোর্ডটা ভেঙে অনেকদিন ধরে ঝুলে আছে।',
        'expected_departments': [
            {'category': 'garbage', 'priority': 'high'},
            {'category': 'parks', 'priority': 'low'},
        ],
        'note': 'A week of overflow plus stated mosquito breeding puts garbage at high; a broken hanging signboard threatens nobody and is purely cosmetic, so low. Two genuinely unrelated crews.',
        'lang': 'bn',
        'tags': ['obvious_split', 'priority_independent'],
    },

    # 12. English - critical contaminated water + low flickering light
    {
        'text': 'Brown, foul-smelling water has been coming from all the taps in our building since this morning and two children in the block have already had stomach upset. Separately, the streetlight at our gate flickers on and off all night.',
        'expected_departments': [
            {'category': 'water_supply', 'priority': 'critical'},
            {'category': 'streetlights', 'priority': 'low'},
        ],
        'note': 'Contaminated supply is high on its own, escalated one level to critical because illness has ALREADY occurred, not merely been risked. The flickering lamp still lights the gate and endangers nobody -- low. The word "Separately" makes the split unambiguous.',
        'lang': 'en',
        'tags': ['obvious_split', 'priority_independent'],
    },

    # 13. Bengali - critical open manhole + low overgrown grass
    {
        'text': 'রাস্তার মাঝখানে ম্যানহোলের ঢাকনা নেই, রাতে কিছুই দেখা যায় না, যে কেউ পড়ে যেতে পারে। আর পাশের মাঠের ঘাস অনেক বড় হয়ে গেছে, কেউ কাটতে আসে না।',
        'expected_departments': [
            {'category': 'drainage', 'priority': 'high'},
            {'category': 'parks', 'priority': 'low'},
        ],
        'note': 'HIGH, not critical: the rubric lists "an uncovered fall-in risk" explicitly as a high example, and no escalation has fired here (nobody has fallen, no multi-day neglect stated), so the tie-break-down rule settles it at high. Drainage owns the chamber. Uncut grass is a routine maintenance backlog, low -- still a two-level gap for the independence test.',
        'lang': 'bn',
        'tags': ['obvious_split', 'priority_independent'],
        'borderline': True,
        'borderline_note': 'Defensible at critical on a "someone could be seriously hurt tonight" reading. Held at high because the rubric names uncovered fall-in risk as a high exemplar and because over-escalation is the measured failure mode. If a case elsewhere states someone HAS fallen in, that one escalates to critical.',
    },

    # ---------------------------------------------------------------
    # Slots 14-17 -- 2-way split, obvious / unrelated dispatch
    # ---------------------------------------------------------------

    # 14. Hinglish - whole-lane lights out + garbage truck missing
    {
        'text': 'Hamare 6th cross me pichle das din se puri gali ki street lights nahi jal rahi, raat me bilkul andhera rehta hai. Aur kachra gaadi bhi ek hafte se nahi aayi, saara kooda corner pe pada hai.',
        'expected_departments': [
            {'category': 'streetlights', 'priority': 'high'},
            {'category': 'garbage', 'priority': 'high'},
        ],
        'note': 'The canonical obvious split -- two unrelated crews, nothing causal between them. Whole-lane blackout for ten days is an area outage (high); a week of uncollected waste piling up is high. Both landing on high is fine here; priority independence is tested in 10-13.',
        'lang': 'hinglish',
        'tags': ['obvious_split'],
    },

    # 15. Hinglish - no water tanker + broken footpath slabs
    {
        'text': 'Colony me pani ka tanker do din se nahi aaya hai, sab log pareshan hain. Aur school ke saamne footpath ke slab toot gaye hain, bachche usi pe chalte hain.',
        'expected_departments': [
            {'category': 'water_supply', 'priority': 'high'},
            {'category': 'roads', 'priority': 'medium'},
        ],
        'note': 'Two days without any supply to the whole colony is a shared-resource disruption plus multi-day duration, so high. The broken footpath slabs are a real trip hazard but nothing states anyone has tripped and no multi-day neglect is claimed for them, so the tie-break-down rule holds that half at medium. Unrelated fixes despite sharing a location.',
        'lang': 'hinglish',
        'tags': ['obvious_split', 'priority_independent'],
        'borderline': True,
        'borderline_note': 'The roads half is defensible at high if broken slabs over a drain are read as a fall-in risk rather than a trip hazard; the text does not say what is under them.',
        'also_accept_departments': [
            {'category': 'water_supply', 'priority': 'high'},
            {'category': 'roads', 'priority': 'high'},
        ],
    },

    # 16. English - whole-road lights out + stray dog pack
    {
        'text': 'None of the streetlights on Kaveri Layout Main Road have worked for the past two weeks. On top of that, a pack of stray dogs has started gathering near the bus stop and chased a delivery rider yesterday.',
        'expected_departments': [
            {'category': 'streetlights', 'priority': 'high'},
            {'category': 'other', 'priority': 'medium'},
        ],
        'note': 'Exercises the animal-control rule alongside a clean split: no civic-engineering department owns stray dogs, so that half is "other", and since the dogs chased but did not bite anyone it stays medium rather than high. Two weeks of whole-road blackout is high.',
        'lang': 'en',
        'tags': ['obvious_split'],
    },

    # 17. Hinglish - illegal dumping + leaning electric pole
    {
        'text': 'Khali plot pe log roz kooda phenk rahe hain, ab wo poora dump ban gaya hai aur badbu aati hai. Saath hi bijli ka khamba tedha ho gaya hai, lagta hai kabhi bhi gir jayega.',
        'expected_departments': [
            {'category': 'garbage', 'priority': 'medium'},
            {'category': 'electricity', 'priority': 'high'},
        ],
        'note': 'Note the ordering: the issue mentioned FIRST is the less urgent one. Accumulated illegal dumping with smell but no stated breeding is medium; a pole leaning and expected to fall is an imminent collapse hazard, high. Tests that the model does not just inherit priority from whichever issue leads the sentence.',
        'lang': 'hinglish',
        'tags': ['obvious_split', 'priority_independent'],
    },

    # ---------------------------------------------------------------
    # Slots 18-22 -- 3-way splits
    # ---------------------------------------------------------------

    # 18. English - storm: tree blocking road + sparking wire + carcass
    {
        'text': "After last night's storm a large tree has fallen right across Nehru Road and traffic cannot pass at all. One of the electrical wires it brought down is sparking on the footpath. There is also a dead stray dog near the junction that has been lying there since morning.",
        'expected_departments': [
            {'category': 'roads', 'priority': 'high'},
            {'category': 'electricity', 'priority': 'critical'},
            {'category': 'garbage', 'priority': 'medium'},
        ],
        'note': 'Exercises three separate category rules at once: the tree is categorised by what it blocks (roads, not parks), the carcass is a haulage job (garbage, not sanitation), and the sparking downed wire is electricity at critical. Deliberately NOT collapsed into one storm-damage ticket -- three different crews.',
        'lang': 'en',
        'tags': ['obvious_split'],
    },

    # 19. Marathi - pothole causing falls + blocked drain + lights out
    {
        'text': 'आमच्या भागात रस्त्यावर मोठा खड्डा पडला आहे, दुचाकीस्वार रोज पडत आहेत. शिवाय गटार तुंबले आहे आणि पाणी साचले आहे. आणि रस्त्यावरचे दिवे पण दोन आठवड्यांपासून बंद आहेत.',
        'expected_departments': [
            {'category': 'roads', 'priority': 'high'},
            {'category': 'drainage', 'priority': 'medium'},
            {'category': 'streetlights', 'priority': 'high'},
        ],
        'note': 'Riders falling daily means accidents have already happened, which lifts an ordinary pothole from medium to high. The blocked drain is stagnant but contained (medium), and two weeks of dark road is an area outage (high). Three priorities across three departments in one complaint.',
        'lang': 'mr',
        'tags': ['obvious_split', 'priority_independent'],
    },

    # 20. English - broken park gate + running tap + garbage pile
    {
        'text': 'The park gate on 8th Main has been broken for several weeks now and anyone can walk in at night. The public tap next to it has been running non-stop and wasting water for at least four days. Garbage is also piling up beside the gate because the bin was removed.',
        'expected_departments': [
            {'category': 'parks', 'priority': 'medium'},
            {'category': 'water_supply', 'priority': 'high'},
            {'category': 'garbage', 'priority': 'medium'},
        ],
        'note': 'All three share one location (the park gate) but need three different crews -- shared location is not a reason to merge. Four days of continuous waste is a multi-day unaddressed leak, high. Broken gate and accumulating garbage are both medium.',
        'lang': 'en',
        'tags': ['obvious_split'],
    },

    # 21. Marathi - obvious sparking transformer + 2 ambiguous
    {
        'text': 'ट्रान्सफॉर्मरमधून ठिणग्या उडत आहेत आणि मोठा आवाज येतो, कधीही आग लागेल असे वाटते. बाजूच्या मोकळ्या जागेत कोणीतरी बांधकामाचा राडारोडा टाकला आहे. आणि रात्री तिथे काही लोक दारू पिऊन गोंधळ घालतात.',
        'expected_departments': [
            {'category': 'electricity', 'priority': 'critical'},
            {'category': 'garbage', 'priority': 'medium'},
            {'category': 'other', 'priority': 'low'},
        ],
        'note': 'CONFIDENCE VARIANCE case: item 1 is unambiguous (sparking transformer with fire risk, critical), while items 2 and 3 are genuinely murky -- construction debris as garbage-haulage is arguable, and public drinking/nuisance has no civic-engineering owner so it falls to "other" at low. Expect high model confidence on the first and noticeably lower on the other two.',
        'lang': 'mr',
        'tags': ['confidence_variance'],
        'borderline': True,
        'borderline_note': 'Construction debris (C&D waste) could defensibly be "other" rather than "garbage" if the municipality treats builder-waste removal as a separate licensed service.',
        'also_accept_departments': [
            {'category': 'electricity', 'priority': 'critical'},
            {'category': 'other', 'priority': 'medium'},
            {'category': 'other', 'priority': 'low'},
        ],
    },

    # 22. Hindi - obvious pothole + 2 ambiguous
    {
        'text': 'स्कूल के सामने सड़क पर बड़ा गड्ढा है और रोज़ बच्चे उसमें गिरते हैं। पास में एक पुराना खंडहर मकान है जो कभी भी गिर सकता है। और पार्क में झूले टूटे पड़े हैं, बच्चे फिर भी उन्हीं पर खेलते हैं।',
        'expected_departments': [
            {'category': 'roads', 'priority': 'high'},
            {'category': 'other', 'priority': 'high'},
            {'category': 'parks', 'priority': 'medium'},
        ],
        'note': 'CONFIDENCE VARIANCE: children falling daily makes the pothole clearly high. The derelict building is ambiguous in category (no civic-engineering department owns building safety, so "other") though clearly serious. Broken swings still in use sit between medium and high.',
        'lang': 'hi',
        'tags': ['confidence_variance'],
        'borderline': True,
        'borderline_note': 'Broken swings that children demonstrably still play on are defensible at high on an injury-risk reading rather than medium as a maintenance backlog.',
        'also_accept_departments': [
            {'category': 'roads', 'priority': 'high'},
            {'category': 'other', 'priority': 'high'},
            {'category': 'parks', 'priority': 'high'},
        ],
    },

    # ---------------------------------------------------------------
    # Slots 23-25 -- MAX LIMIT (5 distinct issues, must cap at 4)
    # ---------------------------------------------------------------

    # 23. Hinglish - storm damage, 5 issues -> drop parks
    {
        'text': 'Kal raat ke toofan ke baad hamari colony ki halat kharab hai - ek ped gir gaya hai main road pe aur rasta poora band hai, bijli ka taar toot kar latak raha hai aur spark kar raha hai, paani ki main pipeline toot gayi hai aur poori colony ka paani band ho gaya hai, saari street lights band hain, aur park ke benches ka rang bhi utar gaya hai.',
        'expected_departments': [
            {'category': 'electricity', 'priority': 'critical'},
            {'category': 'roads', 'priority': 'high'},
            {'category': 'water_supply', 'priority': 'high'},
            {'category': 'streetlights', 'priority': 'high'},
        ],
        'note': 'MAX LIMIT: five distinct departments are present (electricity, roads, water_supply, streetlights, parks) and the peeling paint on park benches -- explicitly a cosmetic low, the rubric\'s own example of specific-but-trivial -- is the one dropped to respect the four-department cap. The fifth item is deliberately the UNAMBIGUOUS lowest so the truncation has only one correct answer. Water is high because the whole colony\'s supply is cut, an area outage, not merely a fresh leak.',
        'lang': 'hinglish',
        'tags': ['max_limit'],
    },

    # 24. Tamil - 5 listed issues -> drop parks
    {
        'text': 'எங்கள் பகுதியில் நிறைய பிரச்சனைகள் உள்ளன - சாக்கடை அடைத்து சாலையில் பாய்கிறது, குப்பை ஒரு வாரமாக எடுக்கப்படவில்லை, தெரு விளக்குகள் எதுவும் எரியவில்லை, குடிநீர் மூன்று நாட்களாக வரவில்லை, மேலும் பூங்காவின் கேட் உடைந்து கிடக்கிறது.',
        'expected_departments': [
            {'category': 'drainage', 'priority': 'high'},
            {'category': 'garbage', 'priority': 'high'},
            {'category': 'streetlights', 'priority': 'high'},
            {'category': 'water_supply', 'priority': 'high'},
        ],
        'note': 'MAX LIMIT with an explicitly enumerated list, which baits a one-per-item response. The broken park gate is the lowest-consequence item and is the one dropped. All four kept items are high: sewage on the road, a week of uncollected waste, a total lighting outage, and three days without drinking water.',
        'lang': 'ta',
        'tags': ['max_limit'],
    },

    # 25. Kannada - 5 issues incl. carcass -> drop parks
    {
        'text': 'ನಮ್ಮ ವಾರ್ಡ್‌ನಲ್ಲಿ ತುಂಬಾ ಸಮಸ್ಯೆಗಳಿವೆ - ರಸ್ತೆಯಲ್ಲಿ ದೊಡ್ಡ ಗುಂಡಿ ಬಿದ್ದಿದೆ ಮತ್ತು ಅಪಘಾತಗಳಾಗುತ್ತಿವೆ, ವಿದ್ಯುತ್ ಕಂಬದಿಂದ ವೈರ್ ಜೋತಾಡುತ್ತಿದೆ, ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದೆ, ಸತ್ತ ನಾಯಿ ಮೂರು ದಿನಗಳಿಂದ ಬಿದ್ದಿದೆ, ಮತ್ತು ಉದ್ಯಾನವನದ ಬೆಂಚುಗಳು ಮುರಿದಿವೆ.',
        'expected_departments': [
            {'category': 'roads', 'priority': 'high'},
            {'category': 'electricity', 'priority': 'high'},
            {'category': 'garbage', 'priority': 'high'},
            {'category': 'drainage', 'priority': 'medium'},
        ],
        'note': 'MAX LIMIT with a mixed-priority cap: broken park benches (the only low item) are dropped, and the retained four are not all high -- the blocked drain stays medium, so a model cannot pass this by simply keeping every high. The hanging wire is NOT stated to be sparking, so it is high rather than critical; the three-day carcass is garbage at high on the duration escalation.',
        'lang': 'kn',
        'tags': ['max_limit'],
    },
]
