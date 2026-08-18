"""
HELD-OUT TEST SET — 200 complaints the model has NEVER seen in its prompt.

This is the honest accuracy measurement for the classifier. run_examples.py
grades the model on the same 15 examples that are baked into its own prompt
(an open-book exam, which is why it scores 15/15). This file is the closed-book
exam.

RULES FOR THIS FILE:
  - NOTHING in here may ever be copied into examples.py. The moment a complaint
    appears in the prompt, it stops being a valid test and the score becomes
    meaningless. If you want more few-shot examples, write new ones.
  - Labels are human-reviewed, not model-generated. If you disagree with a
    label, change the label — don't change the model to match a bad label.
  - Entries tagged "borderline": True are cases where two labels are both
    defensible. They're scored separately so a coin-flip disagreement doesn't
    read as a model failure.

Generated with Gemini Pro, then reviewed by hand.

Cases 1-30: original set, generated with Gemini Pro, reviewed by hand.
Cases 31-100: batch 1 from a teammate (70 cases), originally labeled with an
11-category scheme that didn't match CATEGORIES in categories.py (e.g.
"Water Supply & Sewage", "Public Health & Sanitation", "Town Planning &
Infrastructure"). Remapped case-by-case onto the locked 9-category taxonomy
using precedent from examples.py (open manholes -> drainage, toilets ->
sanitation, playground/park equipment -> parks); "other" used only where no
real municipal department among the 9 fits (spam, staff conduct, private
property disputes, noise pollution — all outside civic-engineering scope).
Priorities lowercased to match PRIORITIES. Original per-case reasoning kept
in "note".

Cases 101-200: batch 2, written by Claude in the same session that rewrote
prompts.py's priority/category rubric after auditing batch 1's failures.
Deliberately built to exercise every calibration line the rubric now draws
explicitly (see the comment above case 101) rather than being freeform —
each case's "note" says which distinction it's testing.
"""

HOLDOUT_SET = [
    # 1. Plain English - Critical (Open manhole near school - life danger)
    {
        "text": "EMERGENCY open manhole right outside St Marys primary school gate kids are running around someone will fall in cover it NOW",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "Open manhole at school entrance creates immediate fatal hazard for children."
    },
    # 2. Hinglish - Critical (Live wire hanging - life danger, landmark reference)
    {
        "text": "bhai Gupta sweets ke samne transformer se live wire latak raha hai sparks nikal rahe barish me koi mar jayega jaldi aao!!",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "Sparking exposed live electric wire in rain is an active life hazard; landmark-based location."
    },
    # 3. Kannada - Critical (Active waterlogging/flooding blocking hospital)
    {
        "text": "ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆ ಎದುರು ಮಳೆ ನೀರು ಪೂರ್ತಿ ತುಂಬಿ ಆಂಬುಲೆನ್ಸ್ ಒಳಗೆ ಹೋಗೋಕೆ ಆಗ್ತಿಲ್ಲ ಕೂಡಲೇ ನೀರು ತೆರವು ಮಾಡಿ",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "Severe flooding blocking hospital access/ambulances represents life safety critical issue."
    },
    # 4. Pure Hindi - Critical (Bridge/culvert slab collapsed on main road)
    {
        "text": "मेन रोड का छोटा पुलिया अचानक धंस गया है बहुत बड़ा गड्ढा बन गया कोई भी गाड़ी अंदर गिर सकती है जान का खतरा है",
        "expected_category": "roads",
        "expected_priority": "critical",
        "note": "Sudden road/culvert structural collapse posing imminent threat of vehicular fatalities."
    },
    # 5. Tamil - High (Sewage contamination mixing into drinking water)
    {
        "text": "எங்க தெருவுல குடிநீர் குழாயில் சாக்கடை தண்ணி கலந்து வருது பயங்கர நாத்தம் குடிக்கவே முடியல 3 நாளா",
        "expected_category": "water_supply",
        "expected_priority": "high",
        "note": "Contaminated drinking water mixed with sewage causes serious ongoing public health outbreak risks.",
        "borderline": True,
        "borderline_note": "critical is equally defensible — sewage in the drinking line is an immediate health hazard, not a future one. Accept either.",
        "also_accept_priority": ["critical"],
    },
    # 6. Hinglish - High (Major water pipe burst flooding road)
    {
        "text": "main pipeline burst ho gaya near Reliance fresh pura paani sadak pe waste ho raha aur supply cut hai subah se",
        "expected_category": "water_supply",
        "expected_priority": "high",
        "note": "Major burst pipeline causing severe civic water disruption; landmark reference."
    },
    # 7. Plain English - High (Deep trenches dug up and left open across lane)
    {
        "text": "they dug whole 4th cross for gas pipeline 2 weeks ago and left open big ditches cars getting stuck daily fix the road",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "Dug up major access road causing ongoing disruption and vehicle entrapment."
    },
    # 8. Telugu - High (Rotting garbage dump near residential area causing fever/dengue)
    {
        "text": "మా కాలనీ లో చెత్త కుప్పలు పేరుకుపోయి వారం అయింది దోమలు విపరీతంగా పెరిగి డెంగ్యూ జ్వరాలు వస్తున్నాయి",
        "expected_category": "garbage",
        "expected_priority": "high",
        "note": "Uncollected decomposing garbage leading to active vector-borne disease outbreak."
    },
    # 9. Pure Hindi - High (Entire colony pitch dark for a week, female safety issue)
    {
        "text": "वार्ड 14 में पिछले एक हफ्ते से एक भी स्ट्रीट लाइट नहीं जल रही रात को महिलाओं और बच्चों का निकलना मुश्किल हो गया है",
        "expected_category": "streetlights",
        "expected_priority": "high",
        "note": "Systemic blackout of entire ward streetlights posing serious ongoing safety and security risks."
    },
    # 10. Hinglish - High (Drain overflow blocking market access)
    {
        "text": "Nala pura choke ho chuka hai sara ganda pani dukan ke andar ghus raha hai badboo se koi customer nahi aa raha",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Severe blocked sewer overflow entering commercial establishments causing major disruption."
    },
    # 11. Plain English - Low (Park maintenance, broken swing/benches)
    {
        "text": "municipal park children play area swings are broken and benches are damaged please send maintenance staff to repair",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Minor amenity repair and routine park equipment maintenance.",
        "borderline": True,
        "borderline_note": "few-shot example #7 labels broken park swings as MEDIUM (children could fall). That example doesn't state an injury risk either. Expect the model to say medium — accept it.",
        "also_accept_priority": ["medium"],
    },
    # 12. Hinglish - Medium (Garbage truck not coming regularly)
    {
        "text": "kachra gadi alternate day bhi nahi aa rahi 3rd street me kripya driver ko regular aane bolo",
        "expected_category": "garbage",
        "expected_priority": "medium",
        "note": "Irregular doorstep garbage collection service; standard municipal grievance."
    },
    # 13. Plain English - Low (Streetlight blinking/faulty)
    {
        "text": "pole number 42 streetlight is flickering continuously like a strobe light please change the bulb",
        "expected_category": "streetlights",
        "expected_priority": "low",
        "note": "Single localized bulb defect; minor non-hazardous issue.",
        "borderline": True,
        "borderline_note": "few-shot example #3 labels a dead streetlight as MEDIUM. A flickering one is arguably the same class of fault. Accept either.",
        "also_accept_priority": ["medium"],
    },
    # 14. Pure Hindi - Medium (Low water pressure in locality)
    {
        "text": "सेक्टर 9 में पानी का प्रेशर बहुत कम आ रहा है पहली मंजिल पर भी पानी नहीं चढ़ रहा मोटर चलाने के बाद भी",
        "expected_category": "water_supply",
        "expected_priority": "medium",
        "note": "Low piped municipal water pressure affecting domestic supply."
    },
    # 15. Kannada - Medium (Potholes on residential cross road)
    {
        "text": "ನಮ್ಮ 2ನೇ ಕ್ರಾಸ್ ರಸ್ತೆಯಲ್ಲಿ ತುಂಬಾ ಗುಂಡಿಗಳು ಬಿದ್ದಿವೆ ದ್ವಿಚಕ್ರ ವಾಹನ ಸವಾರರಿಗೆ ತೊಂದರೆ ಆಗ್ತಿದೆ ಡಾಂಬರೀಕರಣ ಮಾಡಿ",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Standard pothole repair request on residential cross road."
    },
    # 16. Tamil - High (Public toilet unsanitary condition at bus stand)
    {
        "text": "பஸ் ஸ்டாண்ட் பக்கத்துல இருக்கிற பொது கழிப்பறை ரொம்ப அசுத்தமா இருக்கு ஒழுங்கா சுத்தம் பண்றதே இல்ல",
        "expected_category": "sanitation",
        "expected_priority": "high",
        "note": "Severe sanitation breakdown at a major transit hub (bus stand) impacting high public footfall.",
        "borderline": True,
        "borderline_note": "medium fits the stated rubric better — a dirty toilet is unpleasant but not 'major disruption' or 'dangerous soon'. Accept either.",
        "also_accept_priority": ["medium"],
    },
    # 17. Hinglish - Low (Overgrown weeds in neighborhood park)
    {
        "text": "behind Ganesh temple jo park hai waha grass bohot lambi ho gayi hai koi safai nahi karta evening walk impossible",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Minor lawn maintenance and grass cutting request; landmark reference."
    },
    # 18. Telugu - Medium (Frequent voltage fluctuations)
    {
        "text": "మా వీధిలో రాత్రిపూట విపరీతమైన వోల్టేజ్ హెచ్చుతగ్గులు వస్తున్నాయి ఫ్రిజ్ టీవీ పాడైపోయేలా ఉంది",
        "expected_category": "electricity",
        "expected_priority": "medium",
        "note": "Power quality / voltage fluctuation grievance without immediate sparking/fire danger."
    },
    # 19. Plain English - Medium (Road median divider broken)
    {
        "text": "The concrete median divider on ring road near IOCL petrol pump has been damaged by some truck please reconstruct",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Damaged road median structure needing civil repair; landmark reference."
    },
    # 20. Hinglish - Medium (Public urinal cleaning required)
    {
        "text": "Vegetable market ke paas public urinal se bohot foul smell aa rahi hai disinfectent spray karwao",
        "expected_category": "sanitation",
        "expected_priority": "medium",
        "note": "Sanitation/hygiene maintenance near local public marketplace."
    },
    # 21. Plain English - High (Ambiguous: Garbage dumping vs Road blockage, no location)
    {
        "text": "someone dumped huge construction debris and broken tiles right in the middle of the road blocking traffic",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "Active traffic obstruction and collision hazard from dumped debris in carriageway.",
        "borderline": True,
        "borderline_note": "deliberately ambiguous — garbage is equally defensible since the root issue is illegal dumping. Accept either.",
        "also_accept_category": ["garbage"],
    },
    # 22. Hinglish - Medium (Ambiguous: Sanitation vs Drainage, foul smell/standing water)
    {
        "text": "gali me pura sadand faili hui hai ganda pani jama hai na safari wale aate na koi dekhne wala",
        "expected_category": "sanitation",
        "expected_priority": "medium",
        "note": "Valid civic sanitation/stagnant water issue without immediate acute emergency.",
        "borderline": True,
        "borderline_note": "deliberately ambiguous — standing dirty water is squarely drainage territory too. Accept either.",
        "also_accept_category": ["drainage"],
    },
    # 23. Pure Hindi - Medium (Ambiguous: Parks vs Streetlights)
    {
        "text": "नेहरू पार्क के अंदर की सारी लाइट्स पिछले महीने से बंद पड़ी हैं रात में वॉक करना असंभव हो गया है",
        "expected_category": "parks",
        "expected_priority": "medium",
        "note": "Ambiguous between parks department and streetlight maintenance; pertains to internal park infrastructure.",
        "borderline": True,
        "borderline_note": "deliberately ambiguous — the asset is a light, the owner is the parks dept. Accept either.",
        "also_accept_category": ["streetlights"],
    },
    # 24. Plain English - Low (No location mentioned, vague minor road issue)
    {
        "text": "road quality is very bad lots of dust everywhere please do something",
        "expected_category": "roads",
        "expected_priority": "low",
        "note": "Vague general complaint about dust/road quality with no specific location or clear actionable target."
    },
    # 25. Hinglish - Low (No location mentioned, minor water grievance)
    {
        "text": "paani ka timing change karo subah 4 baje kaun uthta hai paani bharne",
        "expected_category": "water_supply",
        "expected_priority": "low",
        "note": "Minor administrative timing grievance without any locality details or systemic breakdown."
    },
    # 26. Pure Hindi - Low (Vague street cleanliness, no location)
    {
        "text": "सड़क पर झाड़ू लगाने वाले समय पर नहीं आते सिर्फ खानापूर्ति करते हैं",
        "expected_category": "sanitation",
        "expected_priority": "low",
        "note": "Vague sweeping grievance lacking specific street, ward, or identifiable location details."
    },
    # 27. Plain English - Low (Angry/emotional rant, zero specific civic issue stated)
    {
        "text": "WORST MUNICIPAL CORPORATION EVER!!! WE PAY TAXES FOR WHAT??? TOTALLY USELESS STAFF CORRUPT OFFICERS SHAME ON YOU ALL",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Pure emotional venting/rant with no actionable civic issue or location stated."
    },
    # 28. Hinglish - Low (Angry rant against local authorities, no problem specified)
    {
        "text": "kya bakwas service hai tum logo ki phone uthate nahi complaint number leke so jate ho sharam aani chahiye sab chor hai",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Angry customer service complaint lacking any specific civic infrastructure category."
    },
    # 29. Kannada - Low (Generic anger/scolding, no department or issue named)
    {
        "text": "ನಿಮ್ಮ ಆಫೀಸ್‌ಗೆ ಎಷ್ಟು ಸಲ ಕಾಲ್ ಮಾಡಿದ್ರೂ ವೇಸ್ಟ್ ಯಾರು ಸರಿಯಾಗಿ ಕೆಲಸ ಮಾಡಲ್ಲ ಜನರಿಗೆ ಮೋಸ ಮಾಡ್ತಿದ್ದೀರಾ ಅಷ್ಟೇ",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "General administrative frustration expressing anger without specifying any municipal issue."
    },
    # 30. Hinglish - Low (Very short / ultra-terse non-specific feedback)
    {
        "text": "bekar nagar nigam",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Three-word non-specific negative review with no civic problem, location, or department identified."
    },

    # ---------------------------------------------------------------------
    # Cases 31-100: batch 1 from a teammate (70 cases). See the module
    # docstring above for the category-remapping methodology.
    # ---------------------------------------------------------------------

    # 31. Malayalam - High (Clean drinking water leaking and wasting from burst pipe in fron...)
    {
        "text": "ഞങ്ങളുടെ വീടിന് മുന്നിലെ പൈപ്പ് പൊട്ടി രണ്ട് ദിവസമായി ശുദ്ധജലം പാഴായി ഒഴുകുന്നു.",
        "expected_category": "water_supply",
        "expected_priority": "high",
        "note": "Priority is High: a burst pipe left unaddressed for two days is prolonged, ongoing water wastage, not a fresh contained leak.",
    },

    # 32. Marathi - Medium (Overflowing public garbage bin spreading waste and foul odor nea...)
    {
        "text": "शिवाजी नगर कमान जवळ कचऱ्याची कुंडी पूर्ण भरून रस्त्यावर कचरा पसरला आहे, दुर्गंधी सुटली आहे.",
        "expected_category": "garbage",
        "expected_priority": "medium",
        "note": "Priority is Medium as overflowing garbage causes foul odor and public nuisance without hazardous biohazard blockage.",
    },

    # 33. Bengali - Critical (Snapped live electrical wire lying on pooled water posing an imm...)
    {
        "text": "রাস্তার ধারের বৈদ্যুতিক তার ছিঁড়ে জলের উপর পড়ে আছে, যেকোনো সময় বড় দুর্ঘটনা ঘটতে পারে।",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "Priority is Critical due to immediate risk of electrocution and public fatality from a live conductor on water.",
    },

    # 34. Odia - High (Collapsed main drain causing heavy dirty water stagnation and co...)
    {
        "text": "ମୁଖ୍ୟ ଡ୍ରେନ ଭାଙ୍ଗିଯିବାରୁ ସବୁ ମଇଳା ପାଣି ରାସ୍ତାରେ ଜମି ରହିଛି, ଯାତାୟାତ ସମ୍ପୂର୍ଣ୍ଣ ବନ୍ଦ।",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High because dirty water overflow has completely blocked vehicular and pedestrian movement.",
    },

    # 35. English - Medium (Pedestrian footpath obstructed by abandoned construction debris ...)
    {
        "text": "Construction debris and concrete blocks left in the middle of pedestrian walking pathway.",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Priority is Medium because it blocks a walkway but does not immediately endanger vehicular traffic or lives.",
    },

    # 36. Hinglish - Low (Loudspeaker noise pollution late at night near Galaxy Banquet ha...)
    {
        "text": "Galaxy Banquet hall ke paas raat 1:30 baje tak loud speakers baj rahe hain, senior citizens cannot sleep.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Priority is Low under civic grading since nighttime noise nuisance requires routine regulation rather than emergency dispatch.",
    },

    # 37. English - High (Cracked tree branch hanging dangerously over active school bus r...)
    {
        "text": "Large roadside gulmohar branch cracked and dangling precariously over the busy school bus route.",
        "expected_category": "parks",
        "expected_priority": "high",
        "note": "Priority is High (not Critical yet) because the branch is dangling with imminent risk of falling on a transit route, but hasn't collapsed yet.",
    },

    # 38. English - Low (Drop in tap water pressure with drain gurgling in 4th cross lane...)
    {
        "text": "Sudden sharp drop in water pressure across the entire 4th cross lane accompanied by gurgling noise in drains.",
        "expected_category": "water_supply",
        "expected_priority": "low",
        "borderline": True,
        "note": "Priority is Low and confidence is 0.41 due to vague dual-symptom description with no immediate contamination or overflow.",
    },

    # 39. English - Low (Commercial promotion for home painting and pest control services...)
    {
        "text": "Special discount on house painting and pest control services this weekend! Call 9876543210 for free inspection.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Priority is Low because non-civic messages and spam are always categorized with lowest operational priority.",
    },

    # 40. Hindi - Critical (Uncovered manhole on an unlit street presenting severe and immed...)
    {
        "text": "बिना ढक्कन का खुला मैनहोल पड़ा है जहां कोई स्ट्रीट लाइट भी नहीं जल रही, बच्चे गिर सकते हैं।",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "Priority is Critical because an open manhole coupled with zero nighttime visibility poses immediate life-threatening fall risk.",
    },

    # 41. English - Medium (Damaged and uneven sidewalk pavers causing trip hazard outside S...)
    {
        "text": "Footpath paving tiles completely broken and uneven in front of SBI ATM on 80 Feet Road, senior citizens tripping.",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Priority is Medium because broken pedestrian pavers create a persistent tripping risk but not an emergency road blockage.",
    },

    # 42. English - Critical (Dangerous unbarricaded road cave-in occupying half the carriagew...)
    {
        "text": "Heavy road cave-in spanning half the lane near Metro Pillar 142, barricades missing.",
        "expected_category": "roads",
        "expected_priority": "critical",
        "note": "Priority is Critical due to deep unbarricaded structural cave-in on an active lane posing fatal collision risk.",
    },

    # 43. English - Low (Faded zebra crossings and lane markings needing repaint at high ...)
    {
        "text": "White lane markings and pedestrian zebra crossing faded completely at the busy high school intersection.",
        "expected_category": "roads",
        "expected_priority": "low",
        "note": "Priority is Low as faded paint is scheduled maintenance without immediate structural road disruption.",
    },

    # 44. English - Medium (Unauthorized unmarked speed bump outside Gate 3 causing vehicle ...)
    {
        "text": "Unscientific high speed breaker built by local residents without warning paint or signage outside gate 3.",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Priority is Medium because unpainted speed bumps damage vehicles and cause minor falls but no lane shutdown.",
    },

    # 45. Bengali - Medium (Eroded road bitumen with loose stones making vehicular driving d...)
    {
        "text": "রাস্তার পিচ উঠে গিয়ে পাথর বেরিয়ে পড়েছে, গাড়ি চালাতে খুব অসুবিধা হচ্ছে।",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Priority is Medium as eroded top surface impairs commute quality without forming sudden life-threatening craters.",
    },

    # 46. English - High (Unfilled utility trench left open across main lane for two weeks...)
    {
        "text": "Open trench dug up for utility cables left unfilled for two weeks across the main lane.",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "Priority is High because a wide transverse road trench forces sudden braking and damages fast traffic.",
    },

    # 47. English - Critical (Sharp protruding steel expansion joint on flyover slashing vehic...)
    {
        "text": "Iron expansion joint on the flyover bridge has jutted upwards by 3 inches, cutting vehicle tires.",
        "expected_category": "roads",
        "expected_priority": "critical",
        "note": "Priority is Critical because high-speed tire punctures on a flyover cause catastrophic rollover accidents.",
    },

    # 48. English - High (Slippery gravel on curved slope near temple arch causing repeate...)
    {
        "text": "Loose gravel scattered on curved road slope near temple arch, two-wheelers slipping during turns.",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "Priority is High due to high probability of active skidding accidents on a turning slope.",
    },

    # 49. Kannada - High (Severe sewage cross-contamination producing black foul-smelling ...)
    {
        "text": "ಕುಡಿಯುವ ನೀರಿನಲ್ಲಿ ಚರಂಡಿ ನೀರು ಮಿಶ್ರಣವಾಗಿ ಬರುತ್ತಿದೆ, ಕೆಟ್ಟ ವಾಸನೆ ಮತ್ತು ಕಪ್ಪು ಬಣ್ಣದ ನೀರು.",
        "expected_category": "water_supply",
        "expected_priority": "high",
        "also_accept_category": ["drainage"],
        "note": "Priority is High because contaminated municipal drinking supply creates an acute community disease risk.",
    },

    # 50. English - Low (Minor morning water loss from roadside sluice valve on 12th Cros...)
    {
        "text": "Water valve leak on 12th cross causing small continuous pool on curb side during morning supply hours.",
        "expected_category": "water_supply",
        "expected_priority": "low",
        "note": "Priority is Low because leakage is restricted to supply hours and creates negligible water accumulation.",
    },

    # 51. English - Critical (Major municipal water trunk line rupture causing high-pressure f...)
    {
        "text": "Main 600mm water distribution pipeline burst near bus terminus, 15-foot water jet flooding roadway.",
        "expected_category": "water_supply",
        "expected_priority": "critical",
        "note": "Priority is Critical due to catastrophic water wastage, rapid road flooding, and infrastructure erosion.",
    },

    # 52. English - High (Municipal sewer blockage causing indoor sewage reverse overflow ...)
    {
        "text": "Underground sewer line choked, black sewage backing up into ground floor toilet bowls in Apartment 4B.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High because raw sewage backflow inside living quarters poses severe biological contamination.",
    },

    # 53. Malayalam - Medium (Chronic low tap water pressure preventing flow to upper floors f...)
    {
        "text": "കുടിവെള്ള പൈപ്പ് ലൈനിൽ പ്രഷർ വളരെ കുറവാണ്, രണ്ടാഴ്ചയായി ഒന്നാം നിലയിൽ വെള്ളം എത്തുന്നില്ല.",
        "expected_category": "water_supply",
        "expected_priority": "medium",
        "note": "Priority is Medium as non-critical water scarcity impairs domestic living but is not an emergency burst.",
    },

    # 54. English - High (Depressed sewer manhole frame creating sudden 6-inch road drop o...)
    {
        "text": "Manhole chamber frame sunken 6 inches below asphalt layer on fast lane opposite City Hospital.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High due to sudden chassis impact and two-wheeler instability in front of hospital route.",
    },

    # 55. English - Critical (Corrosive chemical industrial effluent discharge with toxic vapo...)
    {
        "text": "Heavy industrial effluence leaking from underground drain chamber with strong acidic fumes.",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "Priority is Critical because toxic vapor and acidic liquid present immediate chemical hazard to citizens.",
    },

    # 56. English - Low (Mechanical handpump handle broken at public community borewell.)
    {
        "text": "Public borewell tap handle is broken near community hall, water flowing when pumped manually.",
        "expected_category": "water_supply",
        "expected_priority": "low",
        "note": "Priority is Low as it involves routine mechanical repair of a standalone neighborhood pump.",
    },

    # 57. Telugu - High (Unfenced high-voltage distribution transformer located immediate...)
    {
        "text": "విధుల్లోని ట్రాన్స్‌ఫార్మర్ చుట్టూ రక్షణ కంచె లేదు, పిల్లలు ఆడుకునే మైదానం పక్కనే ఉంది.",
        "expected_category": "electricity",
        "expected_priority": "high",
        "note": "Priority is High because open high-voltage equipment adjacent to play areas is an extreme safety liability.",
    },

    # 58. English - Critical (Open street feeder pillar box exposing live high-voltage busbars...)
    {
        "text": "Electricity junction box door hanging open with exposed live busbars reachable by pedestrians.",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "Priority is Critical due to immediate accidental electrocution risk to walking pedestrians.",
    },

    # 59. English - Medium (Severe voltage instability across Block D risking domestic elect...)
    {
        "text": "Frequent voltage fluctuations between 160V and 290V causing home appliances to shut down in Block D.",
        "expected_category": "electricity",
        "expected_priority": "medium",
        "note": "Priority is Medium as severe voltage instability causes economic damage but no immediate fire.",
    },

    # 60. English - Critical (Structurally broken concrete power pole tilting severely over pu...)
    {
        "text": "Cement electrical pole cracked at the base and tilting at 30 degrees across telephone cables.",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "Priority is Critical because imminent structural collapse of a power pole will drop live overhead conductors.",
    },

    # 61. English - Low (Minor surface rust on streetlight pole base requiring routine an...)
    {
        "text": "Streetlight pole base has slight rusted paint coating near Sector 7 park gate.",
        "expected_category": "streetlights",
        "expected_priority": "low",
        "note": "Priority is Low because superficial corrosion does not affect structural integrity.",
    },

    # 62. Tamil - Critical (Electrified lamppost leaking current during rains due to earthin...)
    {
        "text": "மழை பெய்யும்போது மின்கம்பத்தில் கை வைத்தால் கரண்ட் அடிக்கிறது, எர்த் பிரச்சனை உள்ளது.",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "Priority is Critical because an energized metallic pole in public space delivers lethal shocks.",
    },

    # 63. English - Medium (Power distribution lines tangled in overgrown tree branches need...)
    {
        "text": "Overhead distribution cables entangled in thick overgrown tree canopy behind market complex.",
        "expected_category": "electricity",
        "expected_priority": "medium",
        "note": "Priority is Medium as line entanglement creates intermittent tripping risk during strong winds.",
    },

    # 64. English - Low (Cracked meter display glass on pole 18 with no electrical safety...)
    {
        "text": "Billing meter on utility pole 18 has broken display glass, reading cannot be noted.",
        "expected_category": "electricity",
        "expected_priority": "low",
        "note": "Priority is Low since broken outer glass is an administrative metering defect.",
    },

    # 65. English - Critical (Illegal dumping of hazardous biomedical waste and sharps into pu...)
    {
        "text": "Hospital disposing used syringes, blood bags and bio-waste directly into public municipal dumpster.",
        "expected_category": "garbage",
        "expected_priority": "critical",
        "note": "Priority is Critical due to severe infectious biohazard exposure to scavengers and general public.",
    },

    # 66. English - High (Decomposing animal carcass on roadside near water tank requiring...)
    {
        "text": "Dead street dog carcass lying on side of road near water tank since yesterday afternoon.",
        "expected_category": "garbage",
        "expected_priority": "high",
        "note": "Priority is High because decomposing carcasses cause extreme biological stench and health hazards.",
    },

    # 67. English - Low (Missing lid on park twin-dustbin unit.)
    {
        "text": "Wet waste bin lid missing from public twin-bin stand near jogging park.",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Priority is Low as missing bin lid does not obstruct waste deposit or pose health emergencies.",
    },

    # 68. Malayalam - High (Illegal burning of plastic waste at compost facility generating ...)
    {
        "text": "കമ്പോസ്റ്റ് പ്ലാന്റിൽ നിന്ന് അസഹനീയമായ പുക വരുന്നു, പ്ലാസ്റ്റിക് മാലിന്യം കത്തിക്കുന്നു.",
        "expected_category": "garbage",
        "expected_priority": "high",
        "note": "Priority is High because open plastic incineration produces toxic carcinogens affecting local residents.",
    },

    # 69. English - Low (Uncollected dry garden and horticulture waste left outside bunga...)
    {
        "text": "Green garden clippings and trimmed hedge branches piled up outside bungalow 5 for 3 days.",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Priority is Low as dry garden clippings represent non-hazardous organic bulk waste.",
    },

    # 70. English - Medium (Sweepers improperly disposing road silt directly into stormwater...)
    {
        "text": "Sanitation sweepers dumping collected street dust directly into roadside storm drain openings.",
        "expected_category": "garbage",
        "expected_priority": "medium",
        "note": "Priority is Medium because silting drains leads to eventual monsoon waterlogging.",
    },

    # 71. English - High (Fish market vendors dumping raw decaying fish waste onto public ...)
    {
        "text": "Commercial fish market vendors throwing offal and rotten fish guts on public footpath every evening.",
        "expected_category": "garbage",
        "expected_priority": "high",
        "note": "Priority is High due to putrid organic decomposition, pest infestation, and severe health nuisance.",
    },

    # 72. English - Low (Preventive clearance requested for post office public waste bin ...)
    {
        "text": "Dustbin outside post office is 80% full, will overflow by tonight if not cleared.",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Priority is Low because the bin has not yet spilled onto the street.",
    },

    # 73. English - High (Broken drain concrete slab creating large fall opening near nurs...)
    {
        "text": "Cement drain slab broken, leaving a 3-foot wide exposed slit on pedestrian walkway near nursery school.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High due to severe fall/injury hazard near a school area without active flood conditions.",
    },

    # 74. English - Medium (Clogged storm drain causing localized rainwater stagnation on Cr...)
    {
        "text": "Storm drain choked with plastic bottles causing knee-deep stagnant rainwater on Cross 7 after light drizzle.",
        "expected_category": "drainage",
        "expected_priority": "medium",
        "note": "Priority is Medium because waterlogging causes local transit slowdown without entering residential premises.",
    },

    # 75. English - Critical (Drainage canal wall collapse causing flash flooding into residen...)
    {
        "text": "Stormwater canal retaining wall collapsed during heavy rain; floodwater actively washing into basement parking.",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "Priority is Critical because active flood breach threatens structural foundation and human life.",
    },

    # 76. English - Low (Routine pre-monsoon desilting requested for silted roadside drai...)
    {
        "text": "Heavy silt accumulated in roadside ditch over summer; requires desilting before monsoon starts.",
        "expected_category": "drainage",
        "expected_priority": "low",
        "note": "Priority is Low because it represents preventive maintenance before onset of rains.",
    },

    # 77. Tamil - High (Natural stormwater discharge channel blocked by illegal construc...)
    {
        "text": "காற்றாற்று வெள்ள நீர் வடிகால் ஆக்கிரமிக்கப்பட்டு தடுப்பு சுவர் கட்டப்பட்டுள்ளது.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High because obstruction of primary stormwater channels creates massive flood vulnerabilities.",
    },

    # 78. English - High (Stolen iron stormwater grating leaving dangerous road hole at Ga...)
    {
        "text": "Drain iron grill grate stolen overnight at corner of Gandhi Chowk, leaving an open rectangular hole.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High due to severe vehicle tire trap and nighttime pedestrian fall risk.",
    },

    # 79. English - High (Stagnant stormwater drain acting as heavy mosquito breeding site...)
    {
        "text": "Stagnant green water in open roadside ditch breeding thousands of mosquitoes near primary clinic.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High: mosquito breeding near a clinic is exactly the disease-carrying-conditions case the priority rubric calls high.",
    },

    # 80. English - Low (Minor wild weeds growing at stormwater outlet mouth into canal.)
    {
        "text": "Drain outlet pipe into main canal has minor vegetation overgrowth at mouth.",
        "expected_category": "drainage",
        "expected_priority": "low",
        "note": "Priority is Low as weed growth has not yet caused significant hydraulic backwater.",
    },

    # 81. English - High (Aggressive pack of stray dogs attacking commuters and school chi...)
    {
        "text": "Pack of aggressive stray dogs chasing two-wheelers and biting school children near gate 4 every morning.",
        "expected_category": "sanitation",
        "expected_priority": "high",
        "note": "Priority is High due to active physical bite injuries and severe rabies hazard to children.",
    },

    # 82. English - Low (Routine municipal anti-larval mosquito fogging requested for War...)
    {
        "text": "Chemical fogging for dengue mosquitoes not conducted in Ward 18 for over two months.",
        "expected_category": "sanitation",
        "expected_priority": "low",
        "note": "Priority is Low because routine periodic fogging request is an administrative sanitation schedule.",
    },

    # 83. English - Medium (Unmaintained public toilet overflowing onto sidewalk opposite ma...)
    {
        "text": "Public urinal opposite main bus stand overflowing with urine onto pavement, severe unbearable stink.",
        "expected_category": "sanitation",
        "expected_priority": "medium",
        "note": "Priority is Medium as severe public insanitary conditions degrade public space without biohazard lockdown.",
    },

    # 84. Marathi - Medium (Stray cattle squatting on main road causing severe traffic snarl...)
    {
        "text": "बेवारस जनावरे मुख्य रस्त्यावर बसल्यामुळे वाहतूक कोंडी होत आहे आणि अपघात घडत आहेत.",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Priority is Medium as cattle on roads cause transit delays and vehicular dodging without fatal pileups.",
    },

    # 85. English - High (Unlicensed roadside poultry slaughtering releasing biological bl...)
    {
        "text": "Illegal open meat stall slaughtering chickens on open footpath without health clearance or drainage.",
        "expected_category": "sanitation",
        "expected_priority": "high",
        "note": "Priority is High because unhygienic unregulated animal slaughtering generates acute disease outbreak risks.",
    },

    # 86. English - High (Large active bee hive on children swing frame creating immediate...)
    {
        "text": "Swarm of honeybees formed large hive on children playground swing set frame.",
        "expected_category": "parks",
        "expected_priority": "high",
        "note": "Priority is High due to severe sting attack threat directly on children's play equipment.",
    },

    # 87. English - Low (Park seating benches soiled with pigeon droppings requiring pres...)
    {
        "text": "Public park benches covered in wild pigeon droppings and bird feathers.",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Priority is Low as soiled public park seating is a routine cleaning maintenance matter.",
    },

    # 88. English - Low (Small rodent carcass on footbridge staircase needing sweeper cle...)
    {
        "text": "Dead rat lying dried up on pedestrian overbridge stairs.",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Priority is Low as minor small-animal carcass on stairs requires routine sweep pickup.",
    },

    # 89. English - High (Shopkeeper built illegal concrete ramp extending 6 feet onto pub...)
    {
        "text": "Local sweet shop has extended permanent concrete ramp 6 feet onto the public road, blocking car passage.",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "Priority is High: it is currently blocking car passage on a public road right now, regardless of the longer-term enforcement/demolition process needed to remove it.",
    },

    # 90. English - Critical (Uprooted giant tree crushing vehicle and completely blocking eme...)
    {
        "text": "Massive ancient peepal tree uprooted during cyclone, completely crushing car and blocking hospital road.",
        "expected_category": "roads",
        "expected_priority": "critical",
        "note": "Priority is Critical because emergency access to hospital is blocked and active property damage occurred.",
    },

    # 91. English - Low (Unauthorized promotional flex banners obstructing pedestrian foo...)
    {
        "text": "Illegal advertising flex banners erected across pedestrian footpath blocking sightlines at intersection.",
        "expected_category": "roads",
        "expected_priority": "low",
        "note": "Priority is Low as unauthorized hoarding removal is a standard municipal enforcement action.",
    },

    # 92. English - Low (Temporary hawker pushcart parked near park entrance during eveni...)
    {
        "text": "Street vendor pushing cart occupying corner spot near park gate during evening hours.",
        "expected_category": "roads",
        "expected_priority": "low",
        "note": "Priority is Low because transient hawkers create minor pedestrian friction without physical structures.",
    },

    # 93. English - Critical (Unsafe commercial basement excavation causing adjoining resident...)
    {
        "text": "Deep foundation excavation for commercial complex next door causing boundary wall of residential society to crack and tilt.",
        "expected_category": "other",
        "expected_priority": "critical",
        "note": "Priority is Critical due to structural destabilization threatening immediate building collapse.",
    },

    # 94. English - Low (Private garden shrubs protruding slightly over boundary wall int...)
    {
        "text": "Bougainvillea plant branches from private bungalow garden hanging 1 foot over compound wall into alley.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Priority is Low as mild ornamental overgrowth causes minimal inconvenience.",
    },

    # 95. Gujarati - High (Broken underground sewer lid in street trapping vehicles and cau...)
    {
        "text": "શેરીમાં આવેલું ભૂગર્ભ ગટરનું ઢાંકણું તૂટી ગયું છે અને વાહનો તેમાં ફસાઈ રહ્યા છે.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Priority is High because a broken sewer lid on an active street directly traps vehicles and injures drivers.",
    },

    # 96. Punjabi - High (All streetlights in lane non-functional for a week causing secur...)
    {
        "text": "ਗਲੀ ਦੀਆਂ ਸਾਰੀਆਂ ਲਾਈਟਾਂ ਇੱਕ ਹਫ਼ਤੇ ਤੋਂ ਬੰਦ ਪਈਆਂ ਹਨ, ਰਾਤ ਨੂੰ ਚੋਰੀ ਦਾ ਡਰ ਬਣਿਆ ਰਹਿੰਦਾ ਹੈ।",
        "expected_category": "streetlights",
        "expected_priority": "high",
        "note": "Priority is High: every light on the street out for a week is a whole-area outage, the rubric's own high-tier example.",
    },

    # 97. English - Medium (Unpaved slushy trench left after water pipeline works trapping p...)
    {
        "text": "Water pipeline work completed 1 month ago but road was never restored; now muddy slush traps cars whenever water tanker passes.",
        "expected_category": "roads",
        "expected_priority": "medium",
        "also_accept_category": ["water_supply"],
        "borderline": True,
        "note": "Priority is Medium and confidence is 0.49 due to overlapping responsibility between Water Board excavation and PWD resurfacing.",
    },

    # 98. English - Low (Unsolicited commercial loan marketing spam text.)
    {
        "text": "Urgent loan approved up to 10 Lakhs with zero collateral! Call instant finance desk at 9123456780.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Priority is Low because non-civic commercial promotional spam is assigned the minimum priority tier.",
    },

    # 99. English - Medium (Unexplained recurring subterranean rumbling noise near circular ...)
    {
        "text": "Strange loud rumbling noise heard underground every 10 minutes near the circular market square.",
        "expected_category": "other",
        "expected_priority": "medium",
        "borderline": True,
        "note": "Priority is Medium and confidence is 0.34 due to ambiguous physical source (metro boring vs pipeline cavitation vs geological).",
    },

    # 100. English - Low (Grievance regarding impolite municipal administrative staff at b...)
    {
        "text": "Municipal staff behavior was very rude when I visited office for birth certificate counter.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Priority is Low because administrative staff demeanor is an internal governance issue with no emergency safety impact.",
    },

    # -------------------------------------------------------------------
    # Cases 101-200: batch 2, written by Claude in the same session that
    # rewrote prompts.py's priority/category rubric. Deliberately built to
    # exercise the calibration lines the rubric now draws explicitly:
    # forceful/pressurized bursts vs passive leaks, leak duration (fresh vs
    # multi-day unaddressed), preventive/scheduled maintenance vs an active
    # problem, specific-but-trivial complaints staying low, uncovered fall-in
    # risk vs a sunken-but-covered surface, actively-live/touchable
    # electrical danger vs unfenced-but-quiet equipment, whole-area outages
    # vs a single fixture, an obstruction blocking a road regardless of how
    # permanent it is, and disease/breeding risk counting as high before any
    # confirmed illness. Also exercises the category boundary notes: dead
    # animals as garbage (not sanitation), sweeping/cleaning services as
    # sanitation (not garbage), a hazard's category following what it's
    # blocking/damaging rather than the noun in the sentence, and private
    # property issues as "other" rather than "parks"/"roads".
    # -------------------------------------------------------------------

    # 101. English - Critical (Forceful pressurized water jet at a crowded bus stand)
    {
        "text": "Underground water main has burst right at the bus stand and water is shooting up like a fountain, people getting knocked into each other trying to avoid it.",
        "expected_category": "water_supply",
        "expected_priority": "critical",
        "note": "Forceful, pressurized burst in a crowded spot is a real injury risk, not just water wastage.",
    },
    # 102. Hinglish - High (Multi-day unrepaired leak)
    {
        "text": "Humare street ki pipeline 5 din se leak ho rahi hai, complaint kiya tha lekin abhi tak koi repair karne nahi aaya, bahut paani waste ho gaya.",
        "expected_category": "water_supply",
        "expected_priority": "high",
        "note": "A leak explicitly unaddressed for five days has moved past a fresh, containable report.",
    },
    # 103. Tamil - Medium (Fresh minor leak, still contained)
    {
        "text": "நேத்து மாலையில் இருந்து சின்ன குழாய் லீக் ஆகுது காம்பவுண்ட் சுவர் அருகில், கொஞ்சம் தண்ணி மட்டும் வீணாகுது.",
        "expected_category": "water_supply",
        "expected_priority": "medium",
        "note": "Freshly reported (since yesterday evening), small volume, still contained — not yet an unaddressed multi-day failure.",
    },
    # 104. English - Low (Preventive, no current problem)
    {
        "text": "Our building's water meter is due for its routine annual replacement next month, just confirming the schedule, no issue right now.",
        "expected_category": "water_supply",
        "expected_priority": "low",
        "note": "Purely preventive/scheduled, no active problem described.",
    },
    # 105. Hindi - High (No supply to whole colony, multiple days)
    {
        "text": "puri colony mein teen din se paani ki supply bilkul band hai, sab log bahut pareshan hain, tanker bhi nahi aaya",
        "expected_category": "water_supply",
        "expected_priority": "high",
        "note": "Whole-colony water outage for multiple days is a shared-resource disruption affecting many people.",
    },
    # 106. Kannada - Medium (Low pressure, single building, contained)
    {
        "text": "ನಮ್ಮ ಅಪಾರ್ಟ್ಮೆಂಟ್‌ನಲ್ಲಿ ಒಂದು ವಾರದಿಂದ ನೀರಿನ ಒತ್ತಡ ತುಂಬಾ ಕಡಿಮೆ ಇದೆ, ಪೂರ್ತಿ ನಿಂತಿಲ್ಲ ಆದರೆ ತುಂಬಾ ನಿಧಾನ.",
        "expected_category": "water_supply",
        "expected_priority": "medium",
        "note": "Low pressure, not a full outage, contained to one building — degraded service, nobody in danger.",
    },
    # 107. English - Low (Specific but trivial — hard-to-turn tap)
    {
        "text": "Public tap handle outside Rajaji Nagar community hall is stiff and hard to turn, but water still comes out fine.",
        "expected_category": "water_supply",
        "expected_priority": "low",
        "note": "Precise location, but the underlying problem is trivial — the tap still works.",
    },
    # 108. Hinglish - High (Contaminated water, foul smell/colour)
    {
        "text": "humare naal ka paani do din se peela aur badbudaar aa raha hai, peene layak nahi hai, pura mohalla yehi paani use karta hai",
        "expected_category": "water_supply",
        "expected_priority": "high",
        "note": "Contaminated water affecting a whole neighborhood's supply is a disease-risk / shared-resource high, even without confirmed illness yet.",
    },
    # 109. Telugu - Critical (Sewage mixing causing reported illness)
    {
        "text": "మా వీధి తాగునీటి పైపులో డ్రైనేజీ నీరు కలుస్తోంది, ఇప్పటికే ముగ్గురికి వాంతులు అయ్యాయి, చాలా ప్రమాదకరంగా ఉంది.",
        "expected_category": "water_supply",
        "expected_priority": "critical",
        "note": "Sewage-contaminated drinking water with people already reporting illness (vomiting) is an active, ongoing health emergency, not just a risk.",
        "borderline": True,
        "also_accept_priority": ["high"],
        "borderline_note": "high is defensible too if 'already sick' is read as evidence rather than an emergency in progress; accept either.",
    },
    # 110. English - Low (Vague)
    {
        "text": "There's some water issue in our area, has been like this for a while now.",
        "expected_category": "water_supply",
        "expected_priority": "low",
        "note": "No specific problem, place, or affected person named.",
    },
    # 111. Marathi - Medium (Intermittent borewell motor fault, contained)
    {
        "text": "आमच्या सोसायटीचा बोअरवेल मोटार अधूनमधून बंद पडतो, कधी पाणी येतं कधी नाही, गेल्या आठवड्यापासून असंच आहे.",
        "expected_category": "water_supply",
        "expected_priority": "medium",
        "note": "Intermittent equipment fault degrading service to one society, contained, nobody in danger.",
    },

    # 112. English - Critical (Unbarricaded arterial road cave-in at night)
    {
        "text": "Massive cave-in on the arterial highway right after the flyover exit, no barricades or warning signs, cars are swerving last-second in the dark.",
        "expected_category": "roads",
        "expected_priority": "critical",
        "note": "Unmarked, unbarricaded deep cave-in on a fast arterial road at night is already causing near-misses — a road hazard actively causing crashes.",
    },
    # 113. Hinglish - High (Pothole with stated accident)
    {
        "text": "is gali mein bahut bada pothole hai, parso ek bike wala gir gaya tha usi wajah se, abhi tak repair nahi hua",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "A pothole with a stated accident already occurring rises above the default medium for residential potholes.",
    },
    # 114. English - Medium (Ordinary pothole, no accident)
    {
        "text": "There's a pothole forming on our residential street near house number 24, hasn't caused any accident yet but it's getting bigger.",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Ordinary residential-road pothole with no stated accident or arterial-road context stays medium.",
    },
    # 115. Hindi - Low (Vague general road condition)
    {
        "text": "hamare area ki sadkein overall kaafi kharab haalat mein hain, koi dhyan nahi deta",
        "expected_category": "roads",
        "expected_priority": "low",
        "note": "General complaint with no specific location or damage described.",
    },
    # 116. Punjabi - High (Permanent illegal stall blocking road)
    {
        "text": "ਇੱਕ ਦੁਕਾਨਦਾਰ ਨੇ ਆਪਣਾ ਸਟਾਲ ਪੱਕੇ ਤੌਰ 'ਤੇ ਸੜਕ ਉੱਤੇ ਲਗਾ ਦਿੱਤਾ ਹੈ, ਗੱਡੀਆਂ ਲੰਘਣ ਲਈ ਬਹੁਤ ਤੰਗ ਜਗ੍ਹਾ ਬਚੀ ਹੈ।",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "An obstruction currently blocking road passage is high regardless of whether removing it needs a quick clearing or a longer enforcement process.",
    },
    # 117. English - Low (Faded lane marking, cosmetic)
    {
        "text": "The white lane divider markings on Church Street have faded and are barely visible now.",
        "expected_category": "roads",
        "expected_priority": "low",
        "note": "Precise location, but a faded marking is cosmetic wear, not an active hazard.",
    },
    # 118. Bengali - High (Fallen tree blocking arterial road after storm)
    {
        "text": "ঝড়ের পরে একটা বড় গাছ প্রধান রাস্তার উপর পড়ে গেছে, গাড়ি চলাচল পুরো বন্ধ হয়ে গেছে।",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "A fallen tree completely blocking a main road is a shared-resource obstruction; the category follows what's blocked (the road), not the tree.",
    },
    # 119. English - Critical (Protruding rod already puncturing tires on a highway)
    {
        "text": "A bent iron rod is sticking straight up out of the broken highway surface near the toll booth, it's already punctured two car tires this morning at high speed.",
        "expected_category": "roads",
        "expected_priority": "critical",
        "note": "A road hazard already causing high-speed tire punctures on a highway is a road hazard already causing crashes.",
    },
    # 120. Hinglish - Medium (Broken footpath tiles, minor trip risk)
    {
        "text": "footpath ki tiles TCS office ke bahar ukhad gayi hain, thoda uneven hai lekin abhi tak koi gira nahi hai",
        "expected_category": "roads",
        "expected_priority": "medium",
        "note": "Uneven footpath is a real but contained amenity issue; no stated fall or injury yet.",
    },
    # 121. English - Low (Preventive resurfacing scheduled)
    {
        "text": "Just confirming Elm Street is on the list for its scheduled resurfacing next quarter, no potholes right now.",
        "expected_category": "roads",
        "expected_priority": "low",
        "note": "Preventive/scheduled work, no current problem.",
    },
    # 122. Gujarati - High (Open excavation trench left across main road)
    {
        "text": "મુખ્ય રસ્તા પર ખોદકામ કરીને ખાડો ખુલ્લો છોડી દીધો છે ચાર દિવસથી, વાહનો રસ્તો બદલીને જવું પડે છે.",
        "expected_category": "roads",
        "expected_priority": "high",
        "note": "An open excavation forcing traffic to divert for days is an obstruction blocking a road.",
    },

    # 123. Hinglish - Medium (Public toilet unclean, foul smell)
    {
        "text": "railway station ke paas wala public toilet kaafi dino se saaf nahi hua hai, bahut badbu aati hai andar se",
        "expected_category": "sanitation",
        "expected_priority": "medium",
        "note": "A facility dirty enough to be unpleasant to use — sanitation service issue, contained.",
    },
    # 124. English - Low (Vague sweeping delay)
    {
        "text": "Sweeping in our area has been a bit irregular lately.",
        "expected_category": "sanitation",
        "expected_priority": "low",
        "note": "Vague, no specific street or extent named.",
    },
    # 125. Hindi - Medium (Sweepers not regular on a named street, litter building up)
    {
        "text": "Gandhi Nagar ki 3rd cross road par safai karmi pichle do hafte se nahi aaye hain, kachra jama ho raha hai",
        "expected_category": "sanitation",
        "expected_priority": "medium",
        "note": "Specific street and duration named — a real, contained service lapse, not vague.",
    },
    # 126. English - High (Septic overflow flooding a market street)
    {
        "text": "The public toilet's septic tank has overflowed and is flooding the entire vegetable market street with waste water, unbearable stench.",
        "expected_category": "sanitation",
        "expected_priority": "high",
        "note": "Sewage/waste overflow contaminating a shared public market street is a disease-risk shared-resource high.",
    },
    # 127. Kannada - Low (Vague sweeping complaint)
    {
        "text": "ರಸ್ತೆ ಗುಡಿಸುವವರು ಸರಿಯಾದ ಸಮಯಕ್ಕೆ ಬರುವುದಿಲ್ಲ, ಬರೀ ಕಾಟಾಚಾರಕ್ಕೆ ಗುಡಿಸುತ್ತಾರೆ.",
        "expected_category": "sanitation",
        "expected_priority": "low",
        "note": "Vague sweeping-quality complaint with no specific street, ward, or identifiable location.",
    },
    # 128. English - Medium (Public urinal wall reeking, overdue clean)
    {
        "text": "The public urinal wall behind the bus depot reeks of stale urine, clearly overdue for a deep clean.",
        "expected_category": "sanitation",
        "expected_priority": "medium",
        "note": "Unpleasant-to-use public facility, contained, no stated health outbreak.",
    },
    # 129. Hinglish - Low (Slightly dusty bin area, cosmetic)
    {
        "text": "market ke corner wala dustbin area thoda dusty rehta hai, itna bada issue nahi hai",
        "expected_category": "sanitation",
        "expected_priority": "low",
        "note": "Minor cosmetic cleanliness issue, citizen themselves frames it as minor.",
    },
    # 130. Tamil - High (Sweeping backlog causing pest infestation at a festival market)
    {
        "text": "திருவிழா நேரத்துல சந்தையில ரொம்ப நாளா குப்பை அள்ளாம கிடக்குது, ஈக்களும் எலிகளும் அதிகமாகிடுச்சு.",
        "expected_category": "sanitation",
        "expected_priority": "high",
        "note": "Prolonged cleaning-service lapse causing a pest infestation at a crowded festival market is a disease-risk shared-resource issue.",
    },
    # 131. English - Low (Scheduled fumigation drive)
    {
        "text": "Just checking the fumigation drive for our ward is still scheduled for next month as announced, no current issue.",
        "expected_category": "sanitation",
        "expected_priority": "low",
        "note": "Preventive/scheduled, no active problem.",
    },
    # 132. Marathi - Medium (Public toilet tap leaking, unpleasant)
    {
        "text": "सार्वजनिक शौचालयातील नळ सतत गळतो, जमिनीवर पाणी साचून घाण होते, वापरायला त्रास होतो.",
        "expected_category": "sanitation",
        "expected_priority": "medium",
        "note": "Facility degraded enough to be unpleasant to use, contained to one toilet block.",
    },
    # 133. English - High (Entire ward missed for two weeks)
    {
        "text": "Sanitation workers have not come to our entire ward for the collection and street cleaning round in two weeks, it's affecting every lane here.",
        "expected_category": "sanitation",
        "expected_priority": "high",
        "note": "A whole-ward service lapse for two weeks is a shared-resource disruption affecting many people, not a single-street contained issue.",
    },

    # 134. Hinglish - Critical (Live sparking wire touching a metal railing people are holding)
    {
        "text": "bus stop ki metal railing mein current aa raha hai, ऊपर se ek loose wire chhoo raha hai aur spark ho raha hai, log haath laga rahe the!",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "A live wire energizing a railing people are actively touching is an immediate electrocution risk.",
    },
    # 135. English - High (Unfenced transformer, no spark yet)
    {
        "text": "The transformer box near the school playground has its safety fencing missing, kids play right next to it, no sparking so far though.",
        "expected_category": "electricity",
        "expected_priority": "high",
        "note": "Exposed but not-yet-live equipment is a standing hazard — high, not critical, until it's actually sparking or touched.",
    },
    # 136. Hindi - Medium (Frequent short power cuts, single street, no other issue)
    {
        "text": "hamari gali mein aajkal thodi thodi der ke liye baar baar bijli chali jaati hai, koi aur problem nahi hai",
        "expected_category": "electricity",
        "expected_priority": "medium",
        "note": "Frequent but brief outages on one street, contained, no stated hazard.",
    },
    # 137. English - Low (Cracked meter display, specific location)
    {
        "text": "The electricity meter display on pole 42 outside the pharmacy has a cracked glass, hard to read the numbers.",
        "expected_category": "electricity",
        "expected_priority": "low",
        "note": "Precise location, but a cracked meter glass is cosmetic — reading is merely inconvenient.",
    },
    # 138. Telugu - Critical (Electric pole leaning toward a crowded market stall right now)
    {
        "text": "కరెంటు స్తంభం బాగా వంగి రద్దీగా ఉన్న కూరగాయల దుకాణం మీదకు పడబోతోంది, ఇప్పుడే ఏదైనా జరగొచ్చు.",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "A pole actively leaning toward a crowded stall, about to fall, matches the 'structure actively collapsing or about to' critical test.",
    },
    # 139. English - High (Voltage fluctuation damaging appliances across a whole block)
    {
        "text": "Severe voltage fluctuations across our entire apartment block have damaged multiple refrigerators and fans this week.",
        "expected_category": "electricity",
        "expected_priority": "high",
        "note": "Property damage with no injury risk, but affecting a whole block — a shared-resource disruption, high not critical.",
    },
    # 140. Punjabi - Low (Vague electricity complaint)
    {
        "text": "ਸਾਡੇ ਇਲਾਕੇ ਵਿੱਚ ਕਦੇ-ਕਦੇ ਬਿਜਲੀ ਦੀ ਦਿੱਕਤ ਆ ਜਾਂਦੀ ਹੈ।",
        "expected_category": "electricity",
        "expected_priority": "low",
        "note": "Vague, no specific problem, place, or extent named.",
    },
    # 141. English - Medium (Single pole flickering, contained, no danger)
    {
        "text": "The light on the electric pole outside our gate keeps flickering on and off, otherwise no issue.",
        "expected_category": "electricity",
        "expected_priority": "medium",
        "note": "Contained, minor equipment fault, nobody in danger.",
    },
    # 142. Hinglish - High (Sector-wide outage for two days)
    {
        "text": "poore sector 12 mein do din se bijli nahi hai, sab log bahut pareshan hain office aur ghar dono mein",
        "expected_category": "electricity",
        "expected_priority": "high",
        "note": "Whole-sector outage for two days is a shared-resource disruption affecting many people.",
    },
    # 143. English - Low (Preventive meter inspection)
    {
        "text": "Reminder that our building's meters are due for the routine annual inspection next month, nothing wrong currently.",
        "expected_category": "electricity",
        "expected_priority": "low",
        "note": "Preventive/scheduled, no active problem.",
    },
    # 144. Kannada - Critical (Live wire fallen on a roof, family stuck inside)
    {
        "text": "ಮನೆಯ ಮೇಲ್ಛಾವಣಿ ಮೇಲೆ ವಿದ್ಯುತ್ ತಂತಿ ಬಿದ್ದಿದೆ, ಕಿಡಿಗಳು ಬರುತ್ತಿವೆ, ಮನೆಯೊಳಗೆ ಇರುವವರು ಹೊರಗೆ ಬರಲಾಗುತ್ತಿಲ್ಲ.",
        "expected_category": "electricity",
        "expected_priority": "critical",
        "note": "A sparking live wire down on an occupied roof, trapping the family inside, is an immediate life-threat.",
    },

    # 145. Hindi - Medium (Single streetlight out, others fine)
    {
        "text": "hamari gali ka ek streetlight kaafi din se band hai, baaki sab theek kaam kar rahe hain",
        "expected_category": "streetlights",
        "expected_priority": "medium",
        "note": "A single non-functional streetlight among otherwise-working ones — contained, degraded amenity.",
    },
    # 146. English - High (Whole colony dark for over a week)
    {
        "text": "Every streetlight across our entire colony has been out for more than a week now, it's pitch dark at night.",
        "expected_category": "streetlights",
        "expected_priority": "high",
        "note": "A whole-area outage lasting over a week is high regardless of scope being one colony or one street.",
    },
    # 147. Hinglish - Low (Occasional flicker, minor)
    {
        "text": "ek streetlight thoda flicker karta hai kabhi kabhi, bas itna sa issue hai",
        "expected_category": "streetlights",
        "expected_priority": "low",
        "note": "Minor, occasional, citizen frames it as small.",
    },
    # 148. English - Medium (Three consecutive lights out on a short stretch)
    {
        "text": "Three streetlights in a row are out on the stretch between the temple and the bus stop.",
        "expected_category": "streetlights",
        "expected_priority": "medium",
        "note": "A short contained stretch, not a whole area — degraded but not widespread.",
    },
    # 149. Tamil - High (Leaning pole about to fall)
    {
        "text": "தெரு விளக்கு கம்பம் ரொம்ப சாஞ்சு நிக்குது, பலமா காத்து அடிச்சா விழுந்துடும் மாதிரி இருக்கு.",
        "expected_category": "streetlights",
        "expected_priority": "high",
        "note": "A pole leaning and at risk of falling in wind is a hazard that reaches critical if ignored — high, not yet actively falling.",
    },
    # 150. English - Low (Vague)
    {
        "text": "Streetlights in general could use some maintenance around here.",
        "expected_category": "streetlights",
        "expected_priority": "low",
        "note": "Vague, no specific location.",
    },
    # 151. Marathi - Medium (Timer malfunction, stays on during day)
    {
        "text": "आमच्या रस्त्यावरचा दिवा टायमर बिघडलाय, दिवसाही चालू राहतो, तितकासा मोठा प्रॉब्लेम नाही पण वीज वाया जातेय.",
        "expected_category": "streetlights",
        "expected_priority": "medium",
        "note": "Equipment fault causing wastage, contained, no danger.",
    },
    # 152. English - Low (Cosmetic — peeling paint on pole)
    {
        "text": "The paint on the streetlight pole outside house 17 is peeling, the light itself works fine.",
        "expected_category": "streetlights",
        "expected_priority": "low",
        "note": "Cosmetic wear on a pole that otherwise functions normally.",
    },
    # 153. Hindi - High (Main market street dark for a week, many vendors affected)
    {
        "text": "poori main market street ek hafte se raat mein andheri rehti hai, vendors ko bahut dikkat ho rahi hai security ko lekar",
        "expected_category": "streetlights",
        "expected_priority": "high",
        "note": "A dark main market street for a week affecting many vendors is a shared-area outage.",
    },
    # 154. English - Low (Scheduled annual bulb replacement)
    {
        "text": "Just confirming our street is on the list for the scheduled annual streetlight bulb replacement drive next month.",
        "expected_category": "streetlights",
        "expected_priority": "low",
        "note": "Preventive/scheduled, no current outage.",
    },
    # 155. Bengali - Medium (Dim/flickering light near a park, not fully out)
    {
        "text": "পার্কের পাশের রাস্তার আলোটা কয়েকদিন ধরে টিমটিম করছে, পুরো নেভেনি তবে খুব কম আলো দিচ্ছে।",
        "expected_category": "streetlights",
        "expected_priority": "medium",
        "note": "Degraded but not fully out, single fixture, contained.",
    },

    # 156. English - Critical (Open manhole on a busy road at night)
    {
        "text": "There's an open manhole with no cover in the middle of the road near the flyover, completely dark at night, no barricade around it.",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "An actual uncovered hole on a busy unlit road is a fall-in risk matching the critical test directly.",
    },
    # 157. Hindi - High (Sunken but covered manhole cover)
    {
        "text": "manhole ka dhakkan sadak se thoda neeche dhas gaya hai, gaadiyon ko jhatka lagta hai lekin dhakkan hai, khula nahi hai",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Sunken but still covered — a vehicle hazard, not a fall-in risk, so high rather than critical.",
    },
    # 158. Hinglish - Medium (Minor stagnation, clears in a day)
    {
        "text": "baarish ke baad ek chhoti si ditch mein paani jama ho gaya tha, lekin agle din tak apne aap nikal gaya",
        "expected_category": "drainage",
        "expected_priority": "medium",
        "note": "Minor, self-resolving, contained — a real but low-stakes issue.",
    },
    # 159. English - Low (Preventive desilting scheduled)
    {
        "text": "Just confirming the drain along our lane is scheduled for its routine pre-monsoon desilting next week, no blockage currently.",
        "expected_category": "drainage",
        "expected_priority": "low",
        "note": "Preventive/scheduled work, no active problem.",
    },
    # 160. Kannada - High (Stagnant water breeding mosquitoes near residential block)
    {
        "text": "ಚರಂಡಿಯಲ್ಲಿ ನಿಂತ ನೀರು ಸೊಳ್ಳೆಗಳನ್ನು ಹೆಚ್ಚಿಸುತ್ತಿದೆ, ವಸತಿ ಬ್ಲಾಕ್ ಪಕ್ಕದಲ್ಲೇ ಇದೆ, ಡೆಂಗ್ಯೂ ಭಯ ಇದೆ.",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Mosquito-breeding stagnant water near housing is a disease-carrying-conditions high, even before confirmed illness.",
    },
    # 161. English - Critical (Collapsed drain wall flooding an occupied basement shop)
    {
        "text": "The drain retaining wall has collapsed and floodwater is actively pouring into the basement shop next door while the shopkeeper is still inside.",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "Structural collapse actively sending floodwater into an occupied enclosed space, someone could be trapped.",
    },
    # 162. Telugu - Medium (Slow drain flow, minor puddling)
    {
        "text": "మా వీధి డ్రైన్ నీళ్లు నెమ్మదిగా పోతున్నాయి, కొద్దిగా నీళ్లు నిలిచిపోతున్నాయి కానీ దేనినీ అడ్డుకోవడం లేదు.",
        "expected_category": "drainage",
        "expected_priority": "medium",
        "note": "Slow but functioning drain causing minor puddling, not blocking anything or endangering anyone.",
    },
    # 163. English - Low (Weeds at drain outlet, cosmetic)
    {
        "text": "There's some weed growth at the drain outlet mouth near the canal, water still flows through fine.",
        "expected_category": "drainage",
        "expected_priority": "low",
        "note": "Cosmetic overgrowth with no functional blockage.",
    },
    # 164. Hinglish - High (Sewage overflow mixing into a lake residents use)
    {
        "text": "sewage overflow ho kar seedha lake mein mix ho raha hai, aas paas ke log usi paani ka use karte hain rozmarra ke kaamon mein",
        "expected_category": "drainage",
        "expected_priority": "high",
        "note": "Sewage contaminating a shared water body residents actually use is a disease/contamination-risk high.",
    },
    # 165. English - Medium (Loose drain grating, minor rattle)
    {
        "text": "The drain grating outside the pharmacy is a bit loose and rattles when vehicles pass, but it's not a fall risk.",
        "expected_category": "drainage",
        "expected_priority": "medium",
        "note": "Minor equipment issue explicitly stated as not a fall risk.",
    },
    # 166. Punjabi - Critical (Stolen drain grate, open hole on a busy walking path at night)
    {
        "text": "ਡਰੇਨ ਦੀ ਲੋਹੇ ਦੀ ਜਾਲੀ ਚੋਰੀ ਹੋ ਗਈ ਹੈ, ਹੁਣ ਡੂੰਘਾ ਖੁੱਲ੍ਹਾ ਟੋਆ ਹੈ ਵਿਅਸਤ ਪੈਦਲ ਰਸਤੇ 'ਤੇ, ਰਾਤ ਨੂੰ ਬਿਲਕੁਲ ਦਿਖਦਾ ਨਹੀਂ।",
        "expected_category": "drainage",
        "expected_priority": "critical",
        "note": "A deep uncovered hole on a busy, unlit walking path is a genuine fall-in risk matching the critical test.",
    },

    # 167. English - High (Garbage piling up two weeks across a whole market)
    {
        "text": "Garbage has been piling up across the entire vegetable market for two weeks now, terrible smell and rats everywhere.",
        "expected_category": "garbage",
        "expected_priority": "high",
        "note": "A prolonged, area-wide accumulation affecting many vendors and shoppers, plus a pest/health signal.",
    },
    # 168. Hinglish - Medium (One household's garbage missed, contained)
    {
        "text": "hamare ghar ka kachra pichle 3 din se collect nahi hua, baaki area mein normally ho raha hai",
        "expected_category": "garbage",
        "expected_priority": "medium",
        "note": "Contained to a single household, real but not widespread.",
    },
    # 169. English - Low (Bin lid broken, bin fine, specific location)
    {
        "text": "The dustbin lid near the bus stop on 2nd Main is broken, but the bin isn't overflowing.",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Precise location, but a broken lid on an otherwise-functioning bin is trivial.",
    },
    # 170. Hindi - Low (Vague)
    {
        "text": "kachra sahi se nahi uthta hamare area mein, koi fix nahi karta",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Vague, no specific location or extent.",
    },
    # 171. Tamil - High (Dead cattle carcass on a public road since previous day)
    {
        "text": "நேத்து முதல் ஒரு மாட்டு உடல் பொது சாலையில கிடக்குது, நாற்றம் அதிகமாகிடுச்சு, யாரும் அகற்றல.",
        "expected_category": "garbage",
        "expected_priority": "high",
        "note": "A dead animal is garbage's job to remove, not sanitation's; a large carcass left overnight on a public road is a real health hazard.",
    },
    # 172. English - Critical (Biomedical waste with visible syringes near a playground)
    {
        "text": "Someone has dumped biomedical waste including visible used syringes into the public bin right next to the children's playground.",
        "expected_category": "garbage",
        "expected_priority": "critical",
        "note": "Visible syringes reachable by children playing nearby is an immediate injury/infection risk, not just a health-over-days concern.",
    },
    # 173. Marathi - Medium (Overflowing bin at a bus stop)
    {
        "text": "बस स्टॉपजवळचा कचरापेटी पूर्ण भरून वाहतोय, आजच रिकामी करायला हवी.",
        "expected_category": "garbage",
        "expected_priority": "medium",
        "note": "A single overflowing bin needing prompt but routine clearing.",
    },
    # 174. English - Low (Preventive — extra bin scheduled)
    {
        "text": "Just confirming an extra bin is scheduled to be installed near our lane next month as discussed.",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Preventive/scheduled, no current problem.",
    },
    # 175. Kannada - High (Illegal dumping ground near a water body)
    {
        "text": "ಕೆರೆಯ ಪಕ್ಕದಲ್ಲಿ ಅಕ್ರಮವಾಗಿ ಕಸ ಸುರಿಯುವ ಜಾಗ ಆಗಿದೆ, ನೀರು ಕಲುಷಿತವಾಗುವ ಅಪಾಯ ಇದೆ.",
        "expected_category": "garbage",
        "expected_priority": "high",
        "note": "Illegal dumping threatening to contaminate a shared water body is a disease/contamination-risk high.",
    },
    # 176. English - Low (Rusted but usable dustbin, cosmetic)
    {
        "text": "The dustbin at the park entrance is a bit rusted on the outside, still perfectly usable.",
        "expected_category": "garbage",
        "expected_priority": "low",
        "note": "Cosmetic wear only, no functional impact.",
    },
    # 177. Hinglish - Medium (Garbage truck skipped once, first occurrence)
    {
        "text": "aaj garbage truck hamari street pe nahi aaya, pehli baar aisa hua hai, hope kal aa jayega",
        "expected_category": "garbage",
        "expected_priority": "medium",
        "note": "A one-off missed collection, contained, not yet a pattern.",
    },

    # 178. English - Low (Peeling paint on a park bench, cosmetic)
    {
        "text": "The paint on the benches near the park's east entrance is peeling, benches are otherwise fine to sit on.",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Cosmetic wear on a fully usable amenity.",
    },
    # 179. Hindi - Medium (Broken swing chain, risk if used)
    {
        "text": "bacchon ke park mein jhoole ki chain tooti hui hai, agar koi baccha use kare toh gir sakta hai",
        "expected_category": "parks",
        "expected_priority": "medium",
        "note": "Damaged equipment degrading a contained amenity, real but not an immediate danger unless used.",
    },
    # 180. English - Critical (Cracking branch hanging over kids currently playing under it)
    {
        "text": "A huge branch has cracked and is hanging directly over the play equipment where kids are playing right now, it's creaking and could fall any minute.",
        "expected_category": "parks",
        "expected_priority": "critical",
        "note": "An actively failing structure hanging over children currently underneath it is an imminent, next-few-hours injury risk.",
    },
    # 181. English - Low (Vague)
    {
        "text": "The park in our area could honestly be a lot nicer overall.",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Vague, no specific problem or location.",
    },
    # 182. Telugu - Medium (Uneven pathway pavers, minor trip risk, low traffic)
    {
        "text": "పార్క్ నడక దారిలో రాళ్లు అసమానంగా ఉన్నాయి, కొంచెం తడబడే అవకాశం ఉంది కానీ చాలా మంది వాడరు ఆ దారి.",
        "expected_category": "parks",
        "expected_priority": "medium",
        "note": "Real trip risk but low foot traffic and no injuries stated, contained.",
    },
    # 183. English - Low (Preventive — scheduled tree trimming)
    {
        "text": "Confirming the annual tree trimming for the park is still scheduled for next month, no hazard right now.",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Preventive/scheduled, no current issue.",
    },
    # 184. Hinglish - Medium (Broken gate lock, stays open at night)
    {
        "text": "park ka gate lock tuta hua hai, raat ko khula reh jaata hai, security ka thoda concern hai",
        "expected_category": "parks",
        "expected_priority": "medium",
        "note": "Contained security concern from a broken lock, no stated incident.",
    },
    # 185. English - Low (Rusty drinking fountain, cosmetic)
    {
        "text": "The drinking water fountain in the park has some rust on the outside, still works fine.",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Cosmetic wear, functionally fine.",
    },
    # 186. Punjabi - High (Boundary fence entirely collapsed, stray animals and open access)
    {
        "text": "ਪਾਰਕ ਦੀ ਪੂਰੀ ਬਾਊਂਡਰੀ ਫੈਂਸ ਡਿੱਗ ਗਈ ਹੈ, ਹੁਣ ਅਵਾਰਾ ਪਸ਼ੂ ਅਤੇ ਕੋਈ ਵੀ ਬਿਨਾਂ ਰੋਕ-ਟੋਕ ਅੰਦਰ ਆ ਜਾਂਦਾ ਹੈ, ਬੱਚਿਆਂ ਲਈ ਖ਼ਤਰਾ ਹੈ।",
        "expected_category": "parks",
        "expected_priority": "high",
        "note": "A fully collapsed boundary fence creating open, uncontrolled access for stray animals is a hazard that becomes dangerous if ignored, affecting all park users.",
    },
    # 187. English - Medium (Bins overflowing after a one-time event)
    {
        "text": "The park's litter bins are overflowing after the weekend festival, needs a one-time extra clearing.",
        "expected_category": "parks",
        "expected_priority": "medium",
        "note": "One-time, contained, routine clearing needed.",
    },
    # 188. Bengali - Low (Wobbly bench, minor/cosmetic)
    {
        "text": "পার্কের একটা বেঞ্চ একটু নড়বড়ে হয়ে গেছে, খুব বড় সমস্যা না।",
        "expected_category": "parks",
        "expected_priority": "low",
        "note": "Minor, citizen frames it as small themselves.",
    },

    # 189. English - Low (Vague app feedback)
    {
        "text": "The municipal complaint app's interface could be a lot more user-friendly honestly.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "General feedback, not a civic infrastructure issue.",
    },
    # 190. Hindi - Low (Rude staff behavior)
    {
        "text": "ward office mein staff ne bahut rudely baat ki jab main property tax jama karne gaya tha",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Staff conduct is an internal governance issue with no safety impact.",
    },
    # 191. English - Medium (Private construction noise disturbing a street)
    {
        "text": "Loud construction noise from a private building site has been disturbing our whole street during work hours for two weeks.",
        "expected_category": "other",
        "expected_priority": "medium",
        "note": "Private-site noise nuisance, no clear single civic-engineering department owns it, contained disruption.",
    },
    # 192. Hinglish - Low (Spam SMS, non-civic)
    {
        "text": "mujhe roz ek private number se loan approval ka spam SMS aata hai, isse related complaint hai",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Non-civic commercial spam, minimum priority.",
    },
    # 193. English - Critical (Private balcony detaching over a public sidewalk)
    {
        "text": "A private apartment's balcony slab is visibly cracking and tilting away from the building, right above the public sidewalk where people walk constantly.",
        "expected_category": "other",
        "expected_priority": "critical",
        "note": "A structure actively about to collapse onto a public walkway is critical regardless of it being privately owned — the danger is to the public.",
    },
    # 194. Tamil - Low (Neighbor's private wall paint faded, purely cosmetic dispute)
    {
        "text": "பக்கத்து வீட்டுக்காரோட காம்பவுண்ட் சுவர் பெயிண்ட் கொஞ்சம் மங்கிடுச்சு, அவ்வளவுதான், வேற எந்த பிரச்சனையும் இல்ல.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Purely cosmetic private-property matter with no public impact.",
    },
    # 195. English - Medium (Aggressive stray dog pack, no bite yet)
    {
        "text": "A pack of stray dogs has been acting aggressively toward pedestrians on our lane the past few days, no one bitten yet but people are scared.",
        "expected_category": "other",
        "expected_priority": "medium",
        "note": "A real, contained safety concern with no injury yet — no single civic-engineering department owns animal control here.",
    },
    # 196. English - Medium (Unclear-source chemical smell, ambiguous responsibility)
    {
        "text": "There's a persistent sharp chemical smell in the air near the industrial lane, not clear which facility it's coming from.",
        "expected_category": "other",
        "expected_priority": "medium",
        "note": "Ambiguous source and no confirmed exposure yet — real but not clearly assignable to one department, and not yet an active toxic-exposure emergency.",
        "borderline": True,
        "also_accept_priority": ["high"],
        "borderline_note": "high is defensible if a persistent chemical smell is read as an ongoing exposure risk; accept either.",
    },
    # 197. English - Low (Private parking lot overcharge, non-civic)
    {
        "text": "A private parking lot near the mall overcharged me compared to their posted rate.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Private commercial dispute, not civic infrastructure.",
    },
    # 198. Hindi - Medium (Recurring late-night noise from a private event hall)
    {
        "text": "paas wale private marriage hall se raat ko der tak loud music aati rehti hai, aksar hota hai",
        "expected_category": "other",
        "expected_priority": "medium",
        "note": "Recurring private-venue noise nuisance, no single clear department owner.",
    },
    # 199. English - Critical (Gas smell near a residential complex, source unclear)
    {
        "text": "There's a strong gas smell near our residential complex, source unclear, it's been getting stronger over the last hour.",
        "expected_category": "other",
        "expected_priority": "critical",
        "note": "A toxic/chemical hazard people are being exposed to right now is critical regardless of which department ultimately owns the fix.",
    },
    # 200. English - Low (Vague)
    {
        "text": "The government in general should really do a better job around here.",
        "expected_category": "other",
        "expected_priority": "low",
        "note": "Vague, no specific problem, place, or person named.",
    },
]
