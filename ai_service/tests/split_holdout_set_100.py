"""
HELD-OUT TEST SET for split_departments() -- 100 blind-labeled complaints.

Built on the same method as the 25-case set (ai_service/tests/split_holdout_set.py):
the rule-coverage and distribution matrices in docs/SPLIT_DEPARTMENTS_DESIGN.md
Section 2, scaled 4x. Same hard rule applies: NOTHING here may be copied into
ai_service/split_examples.py, or the score becomes meaningless.

Schema is identical to the 25-case set -- see that module's docstring for the
full field list and for why confidence/excerpt/location_text are deliberately
NOT labeled here.

DISTRIBUTION (100 slots):
      1- 12  no-split baseline          (12)
     13- 24  no-split, causation trap    (12)  incl. 3 RESOLVED-cause reversals (21-23)
     25- 36  no-split, symptom trap      (12)
     37- 52  2-way, independent priority (16)
     53- 68  2-way, obvious split        (16)
     69- 80  3-way, standard             (12)
     81- 88  3-way, confidence variance   (8)
     89-100  4-way, max limit            (12)
    Split profile: 36 no-split, 32 two-way, 20 three-way, 12 four-way.
    Traps: 24 (12 causation incl. 4 reversals, 12 symptom).

OPEN RULING carried over from the 25-case set (slots 13-24 here): R7 in the
design doc routes pipe-damages-road to water_supply (cause owner) while
CLASSIFICATION_DESIGN.md line 45 routes it to roads (fix owner). These labels
reconcile by leak state -- ACTIVE leak stays with the cause owner, an
already-stopped leak leaves the damage with the fix owner. Slots 21-24 are
deliberately the reversal (cause already fixed) to test both directions.
"""

SPLIT_HOLDOUT_SET_100 = [

    # ================= 1-12: no-split baseline =================

    {'text': 'There is a pothole in our residential lane near the third house, it has been getting deeper since the rain but no vehicle has been damaged so far.',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}],
     'note': 'Ordinary side-lane pothole, no accident stated, so no escalation fires.',
     'lang': 'en', 'tags': ['no_split']},

    {'text': 'Humare ghar ke saamne wali street light parso raat se band ho gayi hai, baaki lane ki lights chal rahi hain.',
     'expected_departments': [{'category': 'streetlights', 'priority': 'medium'}],
     'note': 'One lamp out with the rest of the lane lit is not an area outage; recent enough that duration does not escalate.',
     'lang': 'hinglish', 'tags': ['no_split']},

    {'text': 'आज सुबह से नल से मटमैला और बदबूदार पानी आ रहा है, पूरे बिल्डिंग में यही हाल है।',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}],
     'note': 'Contaminated supply is high on the shared-resource clause even before any illness is reported.',
     'lang': 'hi', 'tags': ['no_split']},

    {'text': 'எங்கள் தெருவில் மூன்று நாட்களாக குப்பை வண்டி வரவில்லை, குப்பை மூலையில் குவிந்து கிடக்கிறது.',
     'expected_departments': [{'category': 'garbage', 'priority': 'medium'}],
     'note': 'A collection backlog with no new consequence stated stays at its base level regardless of the three days.',
     'lang': 'ta', 'tags': ['no_split']},

    {'text': 'ನಮ್ಮ ಪಾರ್ಕಿನ ಮೂಲೆಯಲ್ಲಿರುವ ಜಾರುಬಂಡಿ ಮುರಿದು ಬಹಳ ದಿನಗಳಾಗಿವೆ, ಈಗ ಯಾರೂ ಅಲ್ಲಿಗೆ ಹೋಗುವುದಿಲ್ಲ.',
     'expected_departments': [{'category': 'parks', 'priority': 'low'}],
     'note': 'An already-idle broken fixture nobody uses is the rubric low tier: nothing anyone relies on has been lost.',
     'lang': 'kn', 'tags': ['no_split']},

    {'text': 'మా వీధిలో పారిశుద్ధ్య కార్మికులు వారానికి ఒకసారి మాత్రమే వస్తున్నారు, ప్రతిరోజూ ఊడ్చాలి కదా.',
     'expected_departments': [{'category': 'sanitation', 'priority': 'medium'}],
     'note': 'Sweeping is a service being performed badly, which is sanitation, not garbage. A scheduled service actually degraded is medium.',
     'lang': 'te', 'tags': ['no_split']},

    {'text': 'আমাদের রাস্তার ম্যানহোলের ঢাকনাটা ফেটে গেছে কিন্তু এখনও জায়গায় বসানো আছে, ভেঙে পড়ার আগে বদলে দিন।',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}],
     'note': 'Cover cracked but still in place means nobody is exposed yet, so this is a scheduled replacement, not a fall-in risk.',
     'lang': 'bn', 'tags': ['no_split']},

    {'text': 'आमच्या भागातील रोहित्रातून मोठा आवाज येतो, पण ठिणग्या दिसत नाहीत आणि वीजपुरवठा सुरळीत आहे.',
     'expected_departments': [{'category': 'electricity', 'priority': 'medium'}],
     'note': 'Deliberate contrast to a sparking transformer: noise without sparks or outage has no stated path to harm, so not critical.',
     'lang': 'mr', 'tags': ['no_split']},

    {'text': 'One of the footpath tiles outside the post office is loose and rocks when stepped on, the rest of the footpath is fine.',
     'expected_departments': [{'category': 'roads', 'priority': 'low'}],
     'note': 'One tile out of an otherwise sound footpath is the margin-nobody-depends-on case, so low despite naming an exact spot.',
     'lang': 'en', 'tags': ['no_split']},

    {'text': 'Poore area me roz 6-7 ghante bijli jaati hai, do hafte se yahi chal raha hai, sab pareshan hain.',
     'expected_departments': [{'category': 'electricity', 'priority': 'high'}],
     'note': 'A whole-area supply disruption affecting everyone is high on the shared-resource clause.',
     'lang': 'hinglish', 'tags': ['no_split']},

    {'text': 'गली की नाली से बदबू आ रही है, पानी अभी बह रहा है लेकिन गंदगी किनारे जम गई है।',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}],
     'note': 'Still flowing and contained, no breeding or spread stated, so medium.',
     'lang': 'hi', 'tags': ['no_split']},

    {'text': 'পার্কের বেঞ্চগুলোর রং উঠে গেছে, দেখতে খারাপ লাগে, একটু রং করে দিলে ভালো হয়।',
     'expected_departments': [{'category': 'parks', 'priority': 'low'}],
     'note': 'Peeling paint is the rubric own example of cosmetic; the benches still work.',
     'lang': 'bn', 'tags': ['no_split']},

    # ================= 13-24: causation traps =================
    # 13-20 ACTIVE cause (stays with cause owner). 21-24 RESOLVED (reverses).

    {'text': 'A water main has burst outside the temple and is gushing hard right now, the water is spreading across the road and the tar has started lifting at the edges.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active. Lifting tar is downstream of a leak still running; roads cannot resurface until the water is off.',
     'lang': 'en', 'tags': ['no_split', 'causation_trap']},

    {'text': 'ನಮ್ಮ ರಸ್ತೆಯಲ್ಲಿ ಮೂರು ದಿನಗಳಿಂದ ನೀರಿನ ಪೈಪ್ ಸೋರುತ್ತಿದೆ, ಈಗ ರಸ್ತೆಯಲ್ಲಿ ಬಿರುಕು ಬಿಟ್ಟಿದೆ.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active. Road cracking is damage from the live leak; three days unaddressed escalates the leak itself.',
     'lang': 'kn', 'tags': ['no_split', 'causation_trap']},

    {'text': 'सीवर लाइन फट गई है और गंदा पानी लगातार सड़क पर बह रहा है, सड़क की मिट्टी बहती जा रही है।',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active. Sewage owner keeps it; the eroding road surface is downstream of a break that is still open.',
     'lang': 'hi', 'tags': ['no_split', 'causation_trap']},

    {'text': 'குழாய் உடைந்து தண்ணீர் கசிந்து நடைபாதையின் மண்ணை அரித்துக் கொண்டே இருக்கிறது, இன்னும் நிற்கவில்லை.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active. Explicitly still running, so the footpath erosion is not yet a roads job.',
     'lang': 'ta', 'tags': ['no_split', 'causation_trap']},

    {'text': 'కాలువ పొంగి రోడ్డు అంచు కోతకు గురవుతోంది, నీరు ఇంకా పారుతూనే ఉంది.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active. The eroding road edge belongs to the overflow owner while the overflow continues.',
     'lang': 'te', 'tags': ['no_split', 'causation_trap']},

    {'text': 'चार दिवसांपासून पाण्याची पाईप फुटली आहे, रस्ता खचला आहे आणि अजूनही पाणी वाहत आहे.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active, hardest form: the road has visibly subsided, but the leak is stated to be ongoing.',
     'lang': 'mr', 'tags': ['no_split', 'causation_trap'], 'borderline': True,
     'borderline_note': 'Defensible as a 2-way split once the leak is stopped and the subsided road still needs work; held single because the leak is explicitly still running.'},

    {'text': 'পাইপ ফেটে কাদা জল রাস্তায় ছড়িয়ে পড়ছে, এখনও জল বেরোচ্ছে, রাস্তা পিছল হয়ে গেছে।',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active. Slippery road is a symptom of the live leak; no fall stated so no further escalation.',
     'lang': 'bn', 'tags': ['no_split', 'causation_trap']},

    {'text': 'Pipeline leak ki wajah se road pe kaai jam gayi hai aur log phisal rahe hain, leak abhi bhi chal raha hai.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}],
     'note': 'CAUSATION TRAP, active. People slipping is a near-miss, not a stated injury, so no escalation above the leak base.',
     'lang': 'hinglish', 'tags': ['no_split', 'causation_trap']},

    {'text': 'A pipe leak damaged our road last month. The water department repaired the pipe three weeks ago, but the broken road surface they left behind is still not repaired.',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}],
     'note': 'CAUSATION REVERSAL. The causing leak is explicitly already fixed, so nothing remains for water_supply and the leftover damage is an ordinary roads job.',
     'lang': 'en', 'tags': ['no_split', 'causation_trap', 'resolved_cause']},

    {'text': 'बिजली विभाग ने केबल डालने के लिए सड़क खोदी थी, काम पूरा हो गया लेकिन सड़क वैसी ही खुदी पड़ी है।',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}],
     'note': 'CAUSATION REVERSAL. Electricity caused it but their work is finished; road reinstatement is what physically remains.',
     'lang': 'hi', 'tags': ['no_split', 'causation_trap', 'resolved_cause']},

    {'text': 'ಪೈಪ್ ದುರಸ್ತಿ ಮುಗಿದಿದೆ ಆದರೆ ಕಿತ್ತು ಹಾಕಿದ ಪಾದಚಾರಿ ಮಾರ್ಗದ ಟೈಲ್ಸ್ ಅನ್ನು ಮತ್ತೆ ಹಾಕಿಲ್ಲ.',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}],
     'note': 'CAUSATION REVERSAL. Repair complete; the un-relaid footpath tiles are now purely a roads reinstatement.',
     'lang': 'kn', 'tags': ['no_split', 'causation_trap', 'resolved_cause']},

    {'text': 'ట్రాన్స్‌ఫార్మర్ నుండి ఆయిల్ లీక్ అయి పార్కులోని గడ్డి అంతా చచ్చిపోయింది, లీక్ ఇంకా ఆగలేదు.',
     'expected_departments': [{'category': 'electricity', 'priority': 'medium'}],
     'note': 'CAUSATION TRAP, active, different flavour: the dead grass is downstream of an ongoing equipment leak, so electricity owns it, not parks.',
     'lang': 'te', 'tags': ['no_split', 'causation_trap']},

    # ================= 25-36: symptom traps =================

    {'text': 'మా వీధి కాలువ పూర్తిగా మూసుకుపోయి మురుగు రోడ్డుపై పారుతోంది, దుర్వాసనతో పాటు దోమలు పెరుగుతున్నాయి.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}],
     'note': 'SYMPTOM TRAP. Sewage, smell and mosquitoes are all downstream of one blockage; breeding risk makes it high.',
     'lang': 'te', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'नाली में कचरा फंसकर पानी रुक गया है, ऊपर से और कूड़ा जमा हो रहा है।',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}],
     'note': 'SYMPTOM TRAP. Rubbish inside the drain is part of the drain-clearing job, not a separate collection dispatch.',
     'lang': 'hi', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'சாக்கடை அடைப்பால் தேங்கிய நீரில் கொசு பெருகி, அருகில் உள்ள வீடுகளில் அனைவரும் கடிபடுகிறார்கள்.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}],
     'note': 'SYMPTOM TRAP. Mosquitoes are the symptom; clearing the blockage removes them. Breeding risk alone reaches high.',
     'lang': 'ta', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'নর্দমা বন্ধ থাকায় বৃষ্টি হলেই গলিতে জল জমে যায়, জল নামতে অনেক সময় লাগে।',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}],
     'note': 'SYMPTOM TRAP. Waterlogging is conditional on rain and contained, so medium.',
     'lang': 'bn', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡು ಕೆಸರು ರಸ್ತೆಗೆ ಹರಡಿದೆ, ವಾಹನಗಳು ಜಾರುತ್ತಿವೆ.',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}],
     'note': 'SYMPTOM TRAP. Mud on the road came out of the drain; clearing the drain fixes it. No accident stated.',
     'lang': 'kn', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'The drain outside the shops is choked and dirty water has spread over the pavement, flies are everywhere and shopkeepers are complaining.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}],
     'note': 'SYMPTOM TRAP. Flies and spread water both trace to the choke; vector risk makes it high.',
     'lang': 'en', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'सेप्टिक टँक भरून सांडपाणी अंगणात पसरत आहे आणि दुर्गंधी सुटली आहे.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}],
     'note': 'SYMPTOM TRAP. The smell and wet ground are one overflow; sewage spreading where people walk is a disease risk.',
     'lang': 'mr', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'Naali jam hone se paani road pe aa gaya hai aur usme kachra bhi tair raha hai, badbu bahut hai.',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}],
     'note': 'SYMPTOM TRAP. Floating rubbish is being carried by the blocked drain, not a separate garbage pickup.',
     'lang': 'hinglish', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'The streetlight globe outside our gate shattered and the broken glass pieces are now scattered across the footpath below it.',
     'expected_departments': [{'category': 'streetlights', 'priority': 'medium'}],
     'note': 'SYMPTOM TRAP. The glass came out of the broken lamp; replacing the fitting includes clearing its own debris, so no roads or garbage entry.',
     'lang': 'en', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'कूड़ेदान भर जाने से कचरा चारों तरफ बिखर गया है और कुत्ते उसे और फैला रहे हैं।',
     'expected_departments': [{'category': 'garbage', 'priority': 'high'}],
     'note': 'SYMPTOM TRAP. The scattering and the dogs both follow from the overflowing bin; emptying it resolves all of it. Vector risk lifts it to high.',
     'lang': 'hi', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'పార్కులో చెట్టు విరిగి పడింది, దాని కొమ్మలు నడక దారి అంతా పరుచుకుని ఉన్నాయి.',
     'expected_departments': [{'category': 'parks', 'priority': 'medium'}],
     'note': 'SYMPTOM TRAP. Branches on the park path are part of removing the fallen tree, one job. Tree is inside the park and blocks no road, so parks.',
     'lang': 'te', 'tags': ['no_split', 'symptom_trap']},

    {'text': 'পাবলিক টয়লেটের কমোড বন্ধ হয়ে যাওয়ায় ভেতরে দুর্গন্ধ আর কেউ ব্যবহার করতে পারছে না।',
     'expected_departments': [{'category': 'sanitation', 'priority': 'medium'}],
     'note': 'SYMPTOM TRAP. Smell and unusability are one blockage in a facility sanitation maintains.',
     'lang': 'bn', 'tags': ['no_split', 'symptom_trap']},

    # ================= 37-52: 2-way, independent priority =================

    {'text': 'A live wire is hanging low over the footpath near the school and sparks when the wind blows. Also the paint on the park railing has completely faded.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Widest gap: sparking wire over a school footpath is critical, faded railing paint is cosmetic low.',
     'lang': 'en', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'কল থেকে দুর্গন্ধযুক্ত জল আসছে আর দুটি বাচ্চা অসুস্থ হয়ে পড়েছে। এছাড়া পার্কের একটা বেঞ্চ ভাঙা পড়ে আছে।',
     'expected_departments': [{'category': 'water_supply', 'priority': 'critical'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Contamination is high, escalated to critical because illness has already occurred. Broken bench is low.',
     'lang': 'bn', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'सड़क के बीच मैनहोल का ढक्कन गायब है, रात में दिखता नहीं और कोई भी गिर सकता है। पार्क की घास भी बहुत बढ़ गई है।',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Uncovered fall-in risk is the rubric high exemplar; no fall stated so tie-break holds it at high. Overgrown grass is low.',
     'lang': 'hi', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'ವಿದ್ಯುತ್ ತಂತಿ ತುಂಡಾಗಿ ನೆಲದ ಮೇಲೆ ಬಿದ್ದಿದೆ ಮತ್ತು ಕಿಡಿ ಹಾರುತ್ತಿದೆ. ಜೊತೆಗೆ ಬೀದಿ ದೀಪ ಒಂದು ಮಿನುಗುತ್ತಿದೆ.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'streetlights', 'priority': 'low'}],
     'note': 'A live wire on the ground sparking is critical; a single flickering lamp that still lights is low.',
     'lang': 'kn', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'பழைய சுவர் ஒன்று சாய்ந்து எப்போது வேண்டுமானாலும் இடிந்து விழும் நிலையில் உள்ளது, குழந்தைகள் அருகில் விளையாடுகிறார்கள். குப்பைத் தொட்டியின் மூடியும் உடைந்துள்ளது.',
     'expected_departments': [{'category': 'other', 'priority': 'high'}, {'category': 'garbage', 'priority': 'low'}],
     'note': 'A leaning wall is a structural defect not yet collapsing, so high not critical; no civic-engineering wing owns private wall safety, hence other. Broken bin lid is the rubric own low example.',
     'lang': 'ta', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'रोहित्रातून ठिणग्या उडत आहेत, कधीही आग लागू शकते. आणि उद्यानाचा फलक तुटून लटकत आहे.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Sparking transformer with fire risk is critical; a broken hanging signboard endangers nobody.',
     'lang': 'mr', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'Road beech me dhas gaya hai aur ek auto usme fas gaya, traffic ruk gaya hai. Park ke gate ka rang bhi utar gaya hai.',
     'expected_departments': [{'category': 'roads', 'priority': 'critical'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'A cave-in with a vehicle already stuck is a road hazard actively causing incidents, so critical. Peeling gate paint is low.',
     'lang': 'hinglish', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'కరెంటు స్తంభం రోడ్డుపై పడిపోయింది, తీగలు కూడా కింద ఉన్నాయి. పార్కులో గడ్డి పెరిగిపోయింది.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'A downed pole with wires on the ground is an immediate electrocution risk. Overgrown grass is routine.',
     'lang': 'te', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'The entire block has had no water supply for three days and tankers have not come either. Also one of the lights inside the park is not working.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Whole-block outage for three days is high. A single park light out is a margin nobody depends on.',
     'lang': 'en', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'निर्माण का मलबा पूरी सड़क पर फैला है और गाड़ियाँ निकल नहीं पा रही हैं। ज़ेबरा क्रॉसिंग की पट्टियाँ भी मिट गई हैं।',
     'expected_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'roads', 'priority': 'low'}],
     'note': 'Both halves are roads but at very different urgencies: debris blocking passage is an obstruction (high), faded crossing markings are cosmetic (low). Tests that two entries can share a category.',
     'lang': 'hi', 'tags': ['obvious_split', 'priority_independent', 'same_category_split'],
     'borderline': True,
     'borderline_note': 'Defensible as a single roads entry at high, treating the faded markings as a passing mention rather than a separate request.'},

    {'text': 'নিকাশি উপচে বাড়ির ভেতরে নোংরা জল ঢুকে পড়েছে। আর পার্কের দোলনার চেন ছিঁড়ে গেছে।',
     'expected_departments': [{'category': 'drainage', 'priority': 'critical'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Sewage entering an occupied home is floodwater in an enclosed space, the rubric critical example. Broken swing chain is low.',
     'lang': 'bn', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'ಎರಡು ವಾರಗಳಿಂದ ಇಡೀ ರಸ್ತೆಯ ಬೀದಿ ದೀಪಗಳು ಉರಿಯುತ್ತಿಲ್ಲ. ನಮ್ಮ ಬೀದಿಯ ನಾಮಫಲಕವೂ ಮುರಿದಿದೆ.',
     'expected_departments': [{'category': 'streetlights', 'priority': 'high'}, {'category': 'other', 'priority': 'low'}],
     'note': 'Whole-road blackout for two weeks is an area outage (high). A broken street nameplate is trivial and owned by nobody in the eight service wings.',
     'lang': 'kn', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'ஒரு நாய் இறந்து மூன்று நாட்களாக சாலையோரம் கிடக்கிறது, துர்நாற்றம் வீசுகிறது. பூங்காவின் குழாய் சொட்டுச் சொட்டாக ஒழுகுகிறது.',
     'expected_departments': [{'category': 'garbage', 'priority': 'high'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'A carcass is garbage not sanitation, and three days uncollected escalates it to high. A dripping park tap is trivial.',
     'lang': 'ta', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'रस्त्यावरील खड्ड्यात रोज दुचाकीस्वार पडत आहेत. उद्यानातील झुडुपे खूप वाढली आहेत.',
     'expected_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Riders falling daily is stated harm already occurring, lifting an ordinary pothole to high. Overgrown hedges are routine.',
     'lang': 'mr', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'Kachre ke dher me roz koi aag laga deta hai aur poore mohalle me dhuan bhar jaata hai, saans lena mushkil hai. Park ka jhoola bhi awaaz karta hai.',
     'expected_departments': [{'category': 'garbage', 'priority': 'high'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Burning waste filling a neighbourhood with smoke is a shared-resource health disruption (high); the thing burnt is an uncollected heap so garbage owns it. A squeaky swing is trivial.',
     'lang': 'hinglish', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'నీటిలో మట్టి కలిసి వస్తోంది, తాగడానికి పనికిరావడం లేదు. పార్కు గేటు కీలు వదులైంది.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}, {'category': 'parks', 'priority': 'low'}],
     'note': 'Undrinkable supply is contaminated water, high. A loose gate hinge still holding is low.',
     'lang': 'te', 'tags': ['obvious_split', 'priority_independent']},

    # ================= 53-68: 2-way, obvious split =================

    {'text': 'Hamari gali ki saari street lights das din se band hain aur kachra gaadi bhi hafte bhar se nahi aayi.',
     'expected_departments': [{'category': 'streetlights', 'priority': 'high'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'Whole-lane blackout is an area outage (high); a collection gap with no stated new consequence stays medium.',
     'lang': 'hinglish', 'tags': ['obvious_split']},

    {'text': 'The water tanker has not come to our colony for two days. Separately, the footpath slabs outside the school are broken.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}, {'category': 'roads', 'priority': 'medium'}],
     'note': 'Two days without supply to a whole colony is high; broken slabs with nobody stated hurt tie-break down to medium.',
     'lang': 'en', 'tags': ['obvious_split']},

    {'text': 'हमारी गली की स्ट्रीट लाइट खराब है और आवारा कुत्तों का झुंड भी रोज़ सुबह लोगों के पीछे भागता है।',
     'expected_departments': [{'category': 'streetlights', 'priority': 'medium'}, {'category': 'other', 'priority': 'medium'}],
     'note': 'One lamp is medium; stray dogs chasing but not biting is other at medium per the animal-control rule.',
     'lang': 'hi', 'tags': ['obvious_split']},

    {'text': 'ಖಾಲಿ ನಿವೇಶನದಲ್ಲಿ ಕಸ ಸುರಿಯುತ್ತಿದ್ದಾರೆ, ದೊಡ್ಡ ರಾಶಿಯಾಗಿದೆ. ವಿದ್ಯುತ್ ಕಂಬವೂ ವಾಲಿದೆ, ಯಾವಾಗ ಬೇಕಾದರೂ ಬೀಳಬಹುದು.',
     'expected_departments': [{'category': 'garbage', 'priority': 'medium'}, {'category': 'electricity', 'priority': 'high'}],
     'note': 'Less urgent issue is stated first on purpose. Dumping is medium; a leaning pole expected to fall is high.',
     'lang': 'kn', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'சாக்கடை அடைத்துக் கொண்டது, மேலும் தெரு விளக்கு இரண்டு வாரமாக எரியவில்லை.',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}, {'category': 'streetlights', 'priority': 'medium'}],
     'note': 'Two unrelated crews. Blocked drain contained (medium); a single lamp out, even for two weeks, is not an area outage.',
     'lang': 'ta', 'tags': ['obvious_split']},

    {'text': 'నీటి పైపు లీక్ అవుతోంది, పక్కనే పార్కు గేటు విరిగిపోయింది.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'medium'}, {'category': 'parks', 'priority': 'medium'}],
     'note': 'A freshly reported leak is medium; a broken park gate is a real amenity loss at medium. Nothing links them.',
     'lang': 'te', 'tags': ['obvious_split']},

    {'text': 'রাস্তায় বড় গর্ত হয়েছে আর ভ্যাটের আবর্জনা এক সপ্তাহ ধরে উপচে পড়ছে, ইঁদুর ঘুরছে।',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}, {'category': 'garbage', 'priority': 'high'}],
     'note': 'Pothole with no accident stays medium; a week of overflow with rats present is a vector risk at high.',
     'lang': 'bn', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'गटाराचे पाणी रस्त्यावर आले आहे आणि आमच्या भागात वीजपुरवठा तीन दिवसांपासून खंडित आहे.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'electricity', 'priority': 'high'}],
     'note': 'Sewage on the road is a disease risk; a three-day area power cut is a shared-resource outage. Both high, unrelated crews.',
     'lang': 'mr', 'tags': ['obvious_split']},

    {'text': 'The swings and see-saw in the park are broken. Also the street sweepers have not come to our lane in two weeks.',
     'expected_departments': [{'category': 'parks', 'priority': 'medium'}, {'category': 'sanitation', 'priority': 'medium'}],
     'note': 'Broken play equipment is a real amenity loss; a sweeping beat that stopped running is a service failure. Both medium.',
     'lang': 'en', 'tags': ['obvious_split']},

    {'text': 'Bijli do din se nahi aa rahi aur paani ki supply bhi band hai, dono ek saath.',
     'expected_departments': [{'category': 'electricity', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'high'}],
     'note': 'Two separate utilities both out for two days; simultaneity is coincidence, not causation, so they split.',
     'lang': 'hinglish', 'tags': ['obvious_split']},

    {'text': 'चौराहे पर कूड़ा जमा है और दूसरी तरफ गली की नाली भी जाम है, दोनों अलग जगह हैं।',
     'expected_departments': [{'category': 'garbage', 'priority': 'medium'}, {'category': 'drainage', 'priority': 'medium'}],
     'note': 'Deliberately states the two are in different places, so the garbage is NOT the drain blockage: this splits where slot 26 does not.',
     'lang': 'hi', 'tags': ['obvious_split']},

    {'text': 'ಬೀದಿ ದೀಪ ಉರಿಯುತ್ತಿಲ್ಲ ಮತ್ತು ಪಾದಚಾರಿ ಮಾರ್ಗದ ಕಲ್ಲುಗಳು ಕಿತ್ತು ಹೋಗಿವೆ.',
     'expected_departments': [{'category': 'streetlights', 'priority': 'medium'}, {'category': 'roads', 'priority': 'medium'}],
     'note': 'Two ordinary defects, two crews, neither escalated.',
     'lang': 'kn', 'tags': ['obvious_split']},

    {'text': 'குப்பை வண்டி வரவில்லை, மேலும் குடிநீரில் நிறம் மாறி வருகிறது.',
     'expected_departments': [{'category': 'garbage', 'priority': 'medium'}, {'category': 'water_supply', 'priority': 'high'}],
     'note': 'Discoloured drinking water is contamination (high) regardless of the routine collection gap beside it.',
     'lang': 'ta', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'రోడ్డులో గుంత ఉంది, వీధి దీపం కూడా వెలగడం లేదు.',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}, {'category': 'streetlights', 'priority': 'medium'}],
     'note': 'Short, plain two-issue complaint with no escalating detail on either half.',
     'lang': 'te', 'tags': ['obvious_split']},

    {'text': 'নর্দমা পরিষ্কার হয় না আর পার্কের গেট ভাঙা, দুটোই অনেকদিন ধরে।',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}, {'category': 'parks', 'priority': 'medium'}],
     'note': 'Long-standing but neither has a stated new consequence, so duration does not escalate either half.',
     'lang': 'bn', 'tags': ['obvious_split']},

    {'text': 'वीजेचे तार लोंबकळत आहेत आणि कचराकुंडी भरून वाहत आहे.',
     'expected_departments': [{'category': 'electricity', 'priority': 'high'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'Hanging wires with no spark stated are exposed-but-not-yet-live, so high not critical. Overflowing bin without vector detail stays medium.',
     'lang': 'mr', 'tags': ['obvious_split', 'priority_independent']},

    # ================= 69-80: 3-way standard =================

    {'text': "After the storm a large tree is lying across the main road and traffic cannot pass, a wire it brought down is sparking on the footpath, and a dead dog has been near the junction since morning.",
     'expected_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'electricity', 'priority': 'critical'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'Tree categorised by what it blocks (roads), carcass is garbage, sparking wire is critical. Three crews.',
     'lang': 'en', 'tags': ['obvious_split']},

    {'text': 'रस्त्यावर खड्डा आहे आणि दुचाकीस्वार पडत आहेत, गटार तुंबले आहे, आणि दोन आठवड्यांपासून सर्व पथदिवे बंद आहेत.',
     'expected_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'drainage', 'priority': 'medium'}, {'category': 'streetlights', 'priority': 'high'}],
     'note': 'Falls already happening lift the pothole to high; blocked drain contained at medium; all lights out for two weeks is an area outage at high.',
     'lang': 'mr', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'पानी तीन दिन से नहीं आ रहा, कूड़ा भी नहीं उठा, और गली की लाइट भी बंद है।',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}, {'category': 'garbage', 'priority': 'medium'}, {'category': 'streetlights', 'priority': 'medium'}],
     'note': 'Three days without water is high; the other two are routine gaps with no new consequence.',
     'lang': 'hi', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'ರಸ್ತೆಯಲ್ಲಿ ಗುಂಡಿ ಬಿದ್ದಿದೆ, ವಿದ್ಯುತ್ ತಂತಿ ಜೋತಾಡುತ್ತಿದೆ, ಮತ್ತು ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದೆ.',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}, {'category': 'electricity', 'priority': 'high'}, {'category': 'drainage', 'priority': 'medium'}],
     'note': 'Hanging wire without sparks is high; the pothole and drain are ordinary medium.',
     'lang': 'kn', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'சாக்கடை அடைத்துள்ளது, குப்பை எடுக்கப்படவில்லை, தெரு விளக்கும் எரியவில்லை.',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}, {'category': 'garbage', 'priority': 'medium'}, {'category': 'streetlights', 'priority': 'medium'}],
     'note': 'Three separate routine failures, none escalated. Tests that a 3-way split does not by itself imply high priorities.',
     'lang': 'ta', 'tags': ['obvious_split']},

    {'text': 'రోడ్డులో పెద్ద గుంత, విద్యుత్ తీగ వేలాడుతోంది, నీటి పైపు లీక్ అవుతోంది - మూడూ వేర్వేరు చోట్ల.',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}, {'category': 'electricity', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'medium'}],
     'note': 'Explicitly states the three are in different places, so the leak is not causing the pothole: this is a genuine 3-way, not a causation trap.',
     'lang': 'te', 'tags': ['obvious_split']},

    {'text': 'আবর্জনা জমে আছে, নর্দমা আলাদা জায়গায় বন্ধ, আর পার্কের দোলনা ভাঙা।',
     'expected_departments': [{'category': 'garbage', 'priority': 'medium'}, {'category': 'drainage', 'priority': 'medium'}, {'category': 'parks', 'priority': 'medium'}],
     'note': 'States the drain and the garbage are in different places, so the symptom rule does not apply.',
     'lang': 'bn', 'tags': ['obvious_split']},

    {'text': 'Light nahi jal rahi, kachra pada hua hai, aur paani bhi nahi aa raha do din se.',
     'expected_departments': [{'category': 'streetlights', 'priority': 'medium'}, {'category': 'garbage', 'priority': 'medium'}, {'category': 'water_supply', 'priority': 'high'}],
     'note': 'Only the water half carries a duration with real consequence, so only it escalates.',
     'lang': 'hinglish', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'The park gate has been broken for weeks, the public tap beside it has been running non-stop for four days, and garbage is piling up where the bin was removed.',
     'expected_departments': [{'category': 'parks', 'priority': 'medium'}, {'category': 'water_supply', 'priority': 'high'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'One location, three crews. Four days of continuous waste escalates the tap; the other two stay medium.',
     'lang': 'en', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'सड़क टूटी है, बिजली का मीटर बॉक्स खुला पड़ा है, और सफाई कर्मचारी नहीं आते।',
     'expected_departments': [{'category': 'roads', 'priority': 'medium'}, {'category': 'electricity', 'priority': 'high'}, {'category': 'sanitation', 'priority': 'medium'}],
     'note': 'An open meter box is exposed electrical equipment, which the rubric puts at high even before anyone is hurt.',
     'lang': 'hi', 'tags': ['obvious_split', 'priority_independent']},

    {'text': 'गटार तुंबले आहे, पथदिवा बंद आहे, आणि कचरा उचलला जात नाही.',
     'expected_departments': [{'category': 'drainage', 'priority': 'medium'}, {'category': 'streetlights', 'priority': 'medium'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'Three routine failures at medium, deliberately flat so a model cannot pass by escalating everything it splits.',
     'lang': 'mr', 'tags': ['obvious_split']},

    {'text': 'ಕುಡಿಯುವ ನೀರು ಬರುತ್ತಿಲ್ಲ, ರಸ್ತೆ ಹಾಳಾಗಿದೆ, ಮತ್ತು ಉದ್ಯಾನದ ಬೇಲಿ ಮುರಿದಿದೆ.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'medium'}, {'category': 'roads', 'priority': 'medium'}, {'category': 'parks', 'priority': 'medium'}],
     'note': 'No duration or harm stated on any of the three, so all sit at their base level.',
     'lang': 'kn', 'tags': ['obvious_split']},

    # ================= 81-88: 3-way, confidence variance =================

    {'text': 'ट्रान्सफॉर्मरमधून ठिणग्या उडत आहेत. बाजूच्या मोकळ्या जागेत बांधकामाचा राडारोडा टाकला आहे. आणि रात्री तिथे लोक दारू पिऊन गोंधळ घालतात.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'garbage', 'priority': 'medium'}, {'category': 'other', 'priority': 'low'}],
     'note': 'One unambiguous critical plus two murky items: C&D debris as garbage-haulage is arguable, and public nuisance has no service-wing owner.',
     'lang': 'mr', 'tags': ['confidence_variance'], 'borderline': True,
     'borderline_note': 'Construction debris is defensibly other rather than garbage if builder-waste removal is a separate licensed service.',
     'also_accept_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'other', 'priority': 'medium'}, {'category': 'other', 'priority': 'low'}]},

    {'text': 'स्कूल के सामने गड्ढे में रोज़ बच्चे गिरते हैं। पास में एक खंडहर मकान कभी भी गिर सकता है। और पार्क के झूले टूटे हैं जिन पर बच्चे अब भी खेलते हैं।',
     'expected_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'other', 'priority': 'high'}, {'category': 'parks', 'priority': 'medium'}],
     'note': 'Children falling daily makes the pothole clearly high; the derelict building is ambiguous in category but clearly serious; broken swings still in use sit between medium and high.',
     'lang': 'hi', 'tags': ['confidence_variance'], 'borderline': True,
     'borderline_note': 'Broken swings children demonstrably still use are defensible at high on an injury-risk reading.',
     'also_accept_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'other', 'priority': 'high'}, {'category': 'parks', 'priority': 'high'}]},

    {'text': 'A live wire is sparking above the lane. A neighbour\'s tree branches are hanging over the public footpath. And someone has set up a tea stall on the pavement without any licence.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'other', 'priority': 'medium'}, {'category': 'other', 'priority': 'low'}],
     'note': 'Obvious critical first, then two other-category items: private vegetation over public space is other per the boundary rule, and unlicensed vending is an enforcement matter at low.',
     'lang': 'en', 'tags': ['confidence_variance']},

    {'text': 'নর্দমার জল রাস্তায় উপচে পড়ছে। গরু রাস্তার মাঝখানে বসে থাকে। আর রাতে লাউডস্পিকার বাজে।',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'roads', 'priority': 'high'}, {'category': 'other', 'priority': 'low'}],
     'note': 'Cattle sitting in the road are an obstruction, so roads under the animal-control exception, not other. Loudspeaker noise has no service-wing owner.',
     'lang': 'bn', 'tags': ['confidence_variance'], 'borderline': True,
     'borderline_note': 'The cattle half is defensible as other if read as an animal-control matter rather than a road obstruction; the obstruction reading is preferred because clearing the road is the physical fix.'},

    {'text': 'குடிநீரில் அழுக்கு கலந்து வருகிறது. அருகில் அனுமதியின்றி கட்டிடம் கட்டுகிறார்கள். பூங்காவின் ஒரு பகுதியை யாரோ ஆக்கிரமித்துள்ளனர்.',
     'expected_departments': [{'category': 'water_supply', 'priority': 'high'}, {'category': 'other', 'priority': 'medium'}, {'category': 'parks', 'priority': 'medium'}],
     'note': 'Contamination is the clear one; unauthorised construction is other (licensing), and park encroachment is ambiguous between parks-asset and other-enforcement.',
     'lang': 'ta', 'tags': ['confidence_variance'], 'borderline': True,
     'borderline_note': 'Park encroachment is defensible as other, since removing an encroacher is enforcement rather than a parks maintenance job.'},

    {'text': 'కరెంటు స్తంభం విరిగి పడింది. పక్కనే ఎవరో చెత్తను తగలబెడుతున్నారు. వీధి కుక్కలు కూడా గుంపుగా తిరుగుతున్నాయి.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'garbage', 'priority': 'high'}, {'category': 'other', 'priority': 'medium'}],
     'note': 'Fallen pole is critical; burning waste is a health disruption at high and the thing burnt is refuse so garbage owns it; roaming dogs with no bite stated are other at medium.',
     'lang': 'te', 'tags': ['confidence_variance']},

    {'text': 'ಮ್ಯಾನ್‌ಹೋಲ್ ತೆರೆದೇ ಇದೆ. ಯಾರೋ ತಮ್ಮ ಮನೆಯ ಚರಂಡಿಯನ್ನು ನೇರವಾಗಿ ರಸ್ತೆಗೆ ಬಿಟ್ಟಿದ್ದಾರೆ. ಬೀದಿಯ ಫಲಕ ಮಾಸಿ ಹೋಗಿದೆ.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'other', 'priority': 'medium'}, {'category': 'other', 'priority': 'low'}],
     'note': 'Open manhole is the clear high; an illegal private drain connection is an enforcement matter (other); a faded sign is trivial.',
     'lang': 'kn', 'tags': ['confidence_variance'], 'borderline': True,
     'borderline_note': 'The illegal connection is defensible as drainage if read as sewer-network work rather than enforcement against the householder.'},

    {'text': 'Transformer se spark nikal raha hai. Ek badi hoarding tedhi ho kar latak rahi hai. Aur park me log kachra phenk kar jaate hain.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'other', 'priority': 'high'}, {'category': 'garbage', 'priority': 'low'}],
     'note': 'Sparking transformer is critical; a leaning hoarding about to fall is a structural risk with no service-wing owner (other, high); casual littering in a park is minor.',
     'lang': 'hinglish', 'tags': ['confidence_variance']},

    # ================= 89-100: 4-way max limit (5+ issues, cap at 4) =================

    {'text': 'Toofan ke baad - ped gir kar main road band hai, bijli ka taar spark kar raha hai, poori colony ka paani band hai, saari street lights band hain, aur park ke benches ka rang utar gaya hai.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'roads', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'high'}, {'category': 'streetlights', 'priority': 'high'}],
     'note': 'MAX LIMIT. Five departments named; peeling bench paint is the unambiguous lowest and is dropped.',
     'lang': 'hinglish', 'tags': ['max_limit']},

    {'text': 'எங்கள் பகுதியில் - சாக்கடை சாலையில் பாய்கிறது, குப்பை ஒரு வாரமாக எடுக்கவில்லை, தெரு விளக்குகள் எதுவும் எரியவில்லை, மூன்று நாட்களாக குடிநீர் இல்லை, பூங்கா வாயில் உடைந்துள்ளது.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'garbage', 'priority': 'medium'}, {'category': 'streetlights', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'high'}],
     'note': 'MAX LIMIT. Broken park gate is dropped as least consequential. Garbage stays medium: a week with no new consequence does not escalate.',
     'lang': 'ta', 'tags': ['max_limit']},

    {'text': 'ನಮ್ಮ ವಾರ್ಡಿನಲ್ಲಿ - ರಸ್ತೆಯಲ್ಲಿ ಗುಂಡಿ ಮತ್ತು ಅಪಘಾತಗಳಾಗುತ್ತಿವೆ, ಕಂಬದಿಂದ ತಂತಿ ಜೋತಾಡುತ್ತಿದೆ, ಚರಂಡಿ ಕಟ್ಟಿಕೊಂಡಿದೆ, ಸತ್ತ ನಾಯಿ ಮೂರು ದಿನಗಳಿಂದ ಬಿದ್ದಿದೆ, ಉದ್ಯಾನದ ಬೆಂಚು ಮುರಿದಿದೆ.',
     'expected_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'electricity', 'priority': 'high'}, {'category': 'garbage', 'priority': 'high'}, {'category': 'drainage', 'priority': 'medium'}],
     'note': 'MAX LIMIT with a mixed-priority cap: the retained four are not all high, so a model cannot pass by keeping only the highs. Broken bench dropped.',
     'lang': 'kn', 'tags': ['max_limit']},

    {'text': 'Our ward has several problems: sewage is flowing across the main road, a live wire is sparking near the bus stop, the borewell has stopped working so nobody has water, two streetlights are out, and the notice board at the park has fallen down.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'electricity', 'priority': 'critical'}, {'category': 'water_supply', 'priority': 'high'}, {'category': 'streetlights', 'priority': 'medium'}],
     'note': 'MAX LIMIT. The fallen notice board is dropped. Note two lamps out is medium, not the area-outage high.',
     'lang': 'en', 'tags': ['max_limit']},

    {'text': 'हमारे इलाके में - सड़क धंस गई है, बिजली का खंभा झुका है, नाली बंद है, कूड़ा नहीं उठता, और पार्क का फाटक टूटा है।',
     'expected_departments': [{'category': 'roads', 'priority': 'high'}, {'category': 'electricity', 'priority': 'high'}, {'category': 'drainage', 'priority': 'medium'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'MAX LIMIT. Broken park gate dropped. A road cave-in is an obstruction/hazard at high; leaning pole high; the other two routine.',
     'lang': 'hi', 'tags': ['max_limit']},

    {'text': 'আমাদের এলাকায় - নর্দমা উপচে পড়ছে, তার ঝুলছে, তিন দিন জল নেই, আবর্জনা জমে আছে, আর পার্কের বেঞ্চ ভাঙা।',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'electricity', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'high'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'MAX LIMIT. Broken bench dropped as the only low-consequence item.',
     'lang': 'bn', 'tags': ['max_limit']},

    {'text': 'आमच्या भागात - रस्त्यावर खड्डे आहेत, वीजेचे तार तुटले आहेत आणि ठिणग्या उडत आहेत, पाणी येत नाही, कचरा उचलला जात नाही, आणि उद्यानातील फलक मोडला आहे.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'roads', 'priority': 'medium'}, {'category': 'water_supply', 'priority': 'medium'}, {'category': 'garbage', 'priority': 'medium'}],
     'note': 'MAX LIMIT where only ONE item is severe: the sparking broken wire is critical, the rest are ordinary. Park signboard dropped. Tests that the cap keeps the most consequential rather than the first four mentioned.',
     'lang': 'mr', 'tags': ['max_limit']},

    {'text': 'మా వార్డులో - మ్యాన్‌హోల్ తెరిచి ఉంది, వీధి దీపాలు ఏవీ వెలగడం లేదు, చెత్త వారం నుండి పేరుకుపోయింది, రోడ్డు పాడైంది, పార్కు గేటు విరిగింది.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'streetlights', 'priority': 'high'}, {'category': 'garbage', 'priority': 'medium'}, {'category': 'roads', 'priority': 'medium'}],
     'note': 'MAX LIMIT. Park gate dropped. Open manhole and a total lighting outage are the two highs.',
     'lang': 'te', 'tags': ['max_limit']},

    {'text': 'There are many issues on our street: a transformer is sparking, the road has caved in and a car got stuck this morning, sewage is overflowing, garbage has not been collected for ten days and rats are around, the streetlights are out, and the park hedge needs trimming.',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'roads', 'priority': 'critical'}, {'category': 'drainage', 'priority': 'high'}, {'category': 'garbage', 'priority': 'high'}],
     'note': 'MAX LIMIT with SIX issues named, the hardest cap: streetlights and the park hedge are both dropped. The cave-in reaches critical because a vehicle is already stuck.',
     'lang': 'en', 'tags': ['max_limit']},

    {'text': 'Hamare area me - manhole khula hai, taar latak raha hai, naali jam hai, paani nahi aa raha, aur park ka board toota hai.',
     'expected_departments': [{'category': 'drainage', 'priority': 'high'}, {'category': 'electricity', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'medium'}, {'category': 'drainage', 'priority': 'medium'}],
     'note': 'MAX LIMIT with TWO drainage entries at different priorities: the open manhole (high) and the jammed drain (medium) are separate chambers needing separate work. Park board dropped.',
     'lang': 'hinglish', 'tags': ['max_limit', 'same_category_split'], 'borderline': True,
     'borderline_note': 'Defensible as a single drainage entry at high if the open manhole and the jammed drain are read as one drainage job on the same network.'},

    {'text': 'हमारी कॉलोनी में - बिजली नहीं है, पानी नहीं है, सड़क टूटी है, नाली जाम है, कूड़ा पड़ा है, और स्ट्रीट लाइट भी बंद है।',
     'expected_departments': [{'category': 'electricity', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'high'}, {'category': 'roads', 'priority': 'medium'}, {'category': 'drainage', 'priority': 'medium'}],
     'note': 'MAX LIMIT with SIX flatly-listed issues and no severity cues at all, forcing the cap to be decided on department consequence alone. Garbage and streetlights dropped as the two least consequential.',
     'lang': 'hi', 'tags': ['max_limit'], 'borderline': True,
     'borderline_note': 'With no severity detail on any item the choice of which two to drop is genuinely arguable; garbage or streetlights could defensibly replace roads or drainage.'},

    {'text': 'আমাদের পাড়ায় অনেক সমস্যা - বিদ্যুতের তার ছিঁড়ে ঝুলছে ও স্ফুলিঙ্গ বেরোচ্ছে, রাস্তায় বড় গর্ত ও দুর্ঘটনা ঘটছে, জল আসছে না, নর্দমা বন্ধ, আর পার্কের আলো নষ্ট।',
     'expected_departments': [{'category': 'electricity', 'priority': 'critical'}, {'category': 'roads', 'priority': 'high'}, {'category': 'water_supply', 'priority': 'medium'}, {'category': 'drainage', 'priority': 'medium'}],
     'note': 'MAX LIMIT. Park light dropped. Sparking snapped wire is critical; accidents already happening lift the pothole to high.',
     'lang': 'bn', 'tags': ['max_limit']},
]
