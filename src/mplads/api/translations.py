"""Static interface translations, shipped with the code.

The interface must not depend on a network call, a paid API, or a running model to render
in a citizen's own language. These bundles are written once, committed, and served
instantly — the LLM is only ever used for *content* that changes with the data (a case
briefing), never for the chrome.

Only languages with a complete bundle are offered. A half-translated language shown in a
picker is worse than one that is honestly absent.
"""

from __future__ import annotations

from mplads.api.strings import UI

HI: dict[str, str] = {
    "nav.monitor": "निगरानी", "nav.intelligence": "विश्लेषण", "nav.trust": "पारदर्शिता",
    "nav.overview": "समग्र दृश्य", "nav.worklist": "जाँच सूची", "nav.trends": "समय-प्रवृत्ति",
    "nav.duplicates": "समान कार्य", "nav.compliance": "अनुपालन",
    "nav.archetypes": "कार्य श्रेणियाँ", "nav.transparency": "डेटा पारदर्शिता",
    "nav.how": "यह कैसे काम करता है",
    "shell.brandSub": "फ़ोरेंसिक निगरानी", "shell.stakeholder": "उपयोगकर्ता दृष्टिकोण",
    "shell.roleSim": "भूमिका अनुकरण — इस प्रारूप में प्रमाणीकरण नहीं है",
    "shell.viewingAs": "देख रहे हैं", "shell.chain": "सीखें, तुलना करें, अनुमान लगाएँ, समझाएँ, प्राथमिकता दें",
    "shell.leadsNotVerdicts": "जाँच के संकेत, कोई निर्णय नहीं। हर कार्रवाई मनुष्य तय करता है।",
    "overview.title": "राष्ट्रीय समग्र दृश्य", "overview.worksMonitored": "निगरानी में कार्य",
    "overview.totalRecommended": "कुल अनुशंसित राशि", "overview.exposure": "जोखिम में राशि",
    "overview.exposureFoot": "पूर्णता-जोखिम भारित — हानि नहीं, व्यय नहीं",
    "overview.leads": "जाँच के संकेत", "overview.byState": "राज्यवार जोखिम राशि (शीर्ष 10, करोड़)",
    "overview.bands": "विश्वास श्रेणियाँ", "overview.archetypes": "पहचानी गई कार्य श्रेणियाँ",
    "overview.completed": "पूर्ण", "overview.open": "प्रगति में",
    "worklist.title": "जाँच सूची",
    "worklist.sub": "ऑडिट-लाभ के अनुसार क्रम — प्राथमिकता × जोखिम राशि × पुष्टि",
    "worklist.search": "विवरण या कार्यान्वयन एजेंसी खोजें", "worklist.allStates": "सभी राज्य",
    "worklist.allBands": "सभी श्रेणियाँ", "worklist.empty": "इन फ़िल्टरों से कोई परिणाम नहीं।",
    "worklist.work": "कार्य", "worklist.state": "राज्य", "worklist.confidence": "विश्वास",
    "worklist.amount": "राशि", "worklist.auditRoi": "ऑडिट-लाभ", "worklist.prev": "पिछला",
    "worklist.next": "अगला", "worklist.page": "पृष्ठ", "worklist.of": "में से",
    "case.title": "प्रकरण फ़ाइल", "case.back": "सूची पर लौटें",
    "case.evidence": "प्रमाण — यह क्यों सामने आया", "case.peerContext": "समकक्ष तुलना",
    "case.nextStep": "अनुशंसित अगला कदम", "case.recommended": "अनुशंसित",
    "case.completionRisk": "पूर्णता जोखिम", "case.corroboration": "पुष्टि",
    "case.families": "श्रेणियाँ", "case.earlyWarning": "पूर्व चेतावनी",
    "case.compliance": "अनुपालन निष्कर्ष", "case.duplicate": "संभावित समान कार्य",
    "case.aiBrief": "एआई सारांश", "case.archetype": "कार्य श्रेणी",
    "case.peerLevel": "तुलना स्तर", "case.peerSize": "समकक्ष समूह का आकार",
    "case.amountPercentile": "राशि प्रतिशतक",
    "banner.hitl": "ये जाँच के संकेत हैं, कोई निर्णय नहीं। हर मद को पारदर्शी और परस्पर पुष्ट "
                   "संकेतों से ऑडिट-लाभ के आधार पर क्रम दिया गया है। इस डेटा में कोई दोष-सूची "
                   "नहीं है — प्रमाण देखकर मनुष्य ही निर्णय लेता है।",
    "common.loading": "जानकारी लोड हो रही है", "common.works": "कार्य", "common.leads": "संकेत",
    "common.language": "भाषा", "common.generating": "सारांश तैयार हो रहा है",
}

BN: dict[str, str] = {
    "nav.monitor": "পর্যবেক্ষণ", "nav.intelligence": "বিশ্লেষণ", "nav.trust": "স্বচ্ছতা",
    "nav.overview": "সামগ্রিক চিত্র", "nav.worklist": "তদন্ত তালিকা", "nav.trends": "সময়-প্রবণতা",
    "nav.duplicates": "অনুরূপ কাজ", "nav.compliance": "সম্মতি",
    "nav.archetypes": "কাজের ধরন", "nav.transparency": "তথ্য স্বচ্ছতা",
    "nav.how": "এটি কীভাবে কাজ করে",
    "shell.brandSub": "ফরেনসিক পর্যবেক্ষণ", "shell.stakeholder": "ব্যবহারকারীর দৃষ্টিভঙ্গি",
    "shell.roleSim": "ভূমিকা অনুকরণ — এই প্রোটোটাইপে প্রমাণীকরণ নেই",
    "shell.viewingAs": "দেখছেন", "shell.chain": "শিখুন, তুলনা করুন, অনুমান করুন, ব্যাখ্যা করুন, অগ্রাধিকার দিন",
    "shell.leadsNotVerdicts": "তদন্তের সূত্র, কোনও রায় নয়। প্রতিটি সিদ্ধান্ত মানুষ নেয়।",
    "overview.title": "জাতীয় সামগ্রিক চিত্র", "overview.worksMonitored": "পর্যবেক্ষণাধীন কাজ",
    "overview.totalRecommended": "মোট সুপারিশকৃত অর্থ", "overview.exposure": "ঝুঁকিতে থাকা অর্থ",
    "overview.exposureFoot": "সমাপ্তি-ঝুঁকি ভারিত — ক্ষতি নয়, ব্যয় নয়",
    "overview.leads": "তদন্তের সূত্র", "overview.byState": "রাজ্যভিত্তিক ঝুঁকি (শীর্ষ ১০, কোটি)",
    "overview.bands": "আস্থার স্তর", "overview.archetypes": "চিহ্নিত কাজের ধরন",
    "overview.completed": "সম্পন্ন", "overview.open": "চলমান",
    "worklist.title": "তদন্ত তালিকা",
    "worklist.sub": "অডিট-লাভ অনুসারে ক্রম — অগ্রাধিকার × ঝুঁকির অর্থ × সমর্থন",
    "worklist.search": "বিবরণ বা বাস্তবায়নকারী সংস্থা খুঁজুন", "worklist.allStates": "সব রাজ্য",
    "worklist.allBands": "সব স্তর", "worklist.empty": "এই ফিল্টারে কোনও ফল নেই।",
    "worklist.work": "কাজ", "worklist.state": "রাজ্য", "worklist.confidence": "আস্থা",
    "worklist.amount": "পরিমাণ", "worklist.auditRoi": "অডিট-লাভ", "worklist.prev": "পূর্ববর্তী",
    "worklist.next": "পরবর্তী", "worklist.page": "পৃষ্ঠা", "worklist.of": "এর মধ্যে",
    "case.title": "কেস ফাইল", "case.back": "তালিকায় ফিরুন",
    "case.evidence": "প্রমাণ — কেন এটি উঠে এল", "case.peerContext": "সমতুল্য তুলনা",
    "case.nextStep": "প্রস্তাবিত পরবর্তী পদক্ষেপ", "case.recommended": "সুপারিশকৃত",
    "case.completionRisk": "সমাপ্তির ঝুঁকি", "case.corroboration": "সমর্থন",
    "case.families": "শ্রেণি", "case.earlyWarning": "পূর্ব সতর্কতা",
    "case.compliance": "সম্মতি পর্যবেক্ষণ", "case.duplicate": "সম্ভাব্য অনুরূপ কাজ",
    "case.aiBrief": "এআই সারসংক্ষেপ", "case.archetype": "কাজের ধরন",
    "case.peerLevel": "তুলনার স্তর", "case.peerSize": "সমতুল্য গোষ্ঠীর আকার",
    "case.amountPercentile": "পরিমাণ শতাংশক",
    "banner.hitl": "এগুলি তদন্তের সূত্র, কোনও রায় নয়। প্রতিটি বিষয় স্বচ্ছ ও পারস্পরিক সমর্থিত "
                   "সংকেত থেকে অডিট-লাভ অনুসারে সাজানো। এই তথ্যে কোনও দোষ-তালিকা নেই — "
                   "প্রমাণ দেখে মানুষই সিদ্ধান্ত নেয়।",
    "common.loading": "তথ্য লোড হচ্ছে", "common.works": "কাজ", "common.leads": "সূত্র",
    "common.language": "ভাষা", "common.generating": "সারসংক্ষেপ তৈরি হচ্ছে",
}

TA: dict[str, str] = {
    "nav.monitor": "கண்காணிப்பு", "nav.intelligence": "பகுப்பாய்வு", "nav.trust": "வெளிப்படைத்தன்மை",
    "nav.overview": "ஒட்டுமொத்தக் காட்சி", "nav.worklist": "விசாரணை பட்டியல்",
    "nav.trends": "கால போக்கு", "nav.duplicates": "ஒத்த பணிகள்", "nav.compliance": "இணக்கம்",
    "nav.archetypes": "பணி வகைகள்", "nav.transparency": "தரவு வெளிப்படைத்தன்மை",
    "nav.how": "இது எவ்வாறு செயல்படுகிறது",
    "shell.brandSub": "தடயவியல் கண்காணிப்பு", "shell.stakeholder": "பயனர் பார்வை",
    "shell.roleSim": "பணி உருவகப்படுத்துதல் — இந்த மாதிரியில் அங்கீகாரம் இல்லை",
    "shell.viewingAs": "பார்க்கிறீர்கள்",
    "shell.chain": "கற்றல், ஒப்பீடு, கணிப்பு, விளக்கம், முன்னுரிமை",
    "shell.leadsNotVerdicts": "விசாரணைக் குறிப்புகள், தீர்ப்புகள் அல்ல. ஒவ்வொரு நடவடிக்கையையும் மனிதரே முடிவு செய்கிறார்.",
    "overview.title": "தேசிய ஒட்டுமொத்தக் காட்சி", "overview.worksMonitored": "கண்காணிக்கப்படும் பணிகள்",
    "overview.totalRecommended": "மொத்த பரிந்துரைத் தொகை", "overview.exposure": "அபாயத்தில் உள்ள தொகை",
    "overview.exposureFoot": "நிறைவு-அபாய அடிப்படையில் — இழப்பு அல்ல, செலவு அல்ல",
    "overview.leads": "விசாரணைக் குறிப்புகள்",
    "overview.byState": "மாநிலவாரி அபாயத் தொகை (முதல் 10, கோடி)",
    "overview.bands": "நம்பிக்கை நிலைகள்", "overview.archetypes": "கண்டறியப்பட்ட பணி வகைகள்",
    "overview.completed": "நிறைவு", "overview.open": "நடைபெறுகிறது",
    "worklist.title": "விசாரணை பட்டியல்",
    "worklist.sub": "தணிக்கை-பயன் அடிப்படையில் வரிசை — முன்னுரிமை × அபாயத் தொகை × உறுதிப்பாடு",
    "worklist.search": "விவரம் அல்லது செயலாக்க நிறுவனத்தைத் தேடுக", "worklist.allStates": "அனைத்து மாநிலங்கள்",
    "worklist.allBands": "அனைத்து நிலைகள்", "worklist.empty": "இந்த வடிகட்டிகளுக்கு முடிவு இல்லை.",
    "worklist.work": "பணி", "worklist.state": "மாநிலம்", "worklist.confidence": "நம்பிக்கை",
    "worklist.amount": "தொகை", "worklist.auditRoi": "தணிக்கை-பயன்", "worklist.prev": "முந்தையது",
    "worklist.next": "அடுத்தது", "worklist.page": "பக்கம்", "worklist.of": "இல்",
    "case.title": "வழக்குக் கோப்பு", "case.back": "பட்டியலுக்குத் திரும்பு",
    "case.evidence": "சான்று — இது ஏன் வெளிவந்தது", "case.peerContext": "ஒப்பீட்டுச் சூழல்",
    "case.nextStep": "பரிந்துரைக்கப்பட்ட அடுத்த படி", "case.recommended": "பரிந்துரைக்கப்பட்டது",
    "case.completionRisk": "நிறைவு அபாயம்", "case.corroboration": "உறுதிப்பாடு",
    "case.families": "வகைகள்", "case.earlyWarning": "முன்னெச்சரிக்கை",
    "case.compliance": "இணக்கக் கண்டுபிடிப்புகள்", "case.duplicate": "ஒத்த பணி வாய்ப்பு",
    "case.aiBrief": "AI சுருக்கம்", "case.archetype": "பணி வகை",
    "case.peerLevel": "ஒப்பீட்டு நிலை", "case.peerSize": "ஒப்பீட்டுக் குழு அளவு",
    "case.amountPercentile": "தொகை சதவீதம்",
    "banner.hitl": "இவை விசாரணைக் குறிப்புகள், தீர்ப்புகள் அல்ல. ஒவ்வொன்றும் வெளிப்படையான, "
                   "பரஸ்பரம் உறுதிசெய்யப்பட்ட சமிக்ஞைகளின் அடிப்படையில் தணிக்கை-பயன்படி "
                   "வரிசைப்படுத்தப்பட்டுள்ளது. இத்தரவில் குற்றப் பட்டியல் இல்லை — சான்றைப் "
                   "பார்த்து மனிதரே முடிவு செய்கிறார்.",
    "common.loading": "தகவல் ஏற்றப்படுகிறது", "common.works": "பணிகள்", "common.leads": "குறிப்புகள்",
    "common.language": "மொழி", "common.generating": "சுருக்கம் தயாராகிறது",
}

TE: dict[str, str] = {
    "nav.monitor": "పర్యవేక్షణ", "nav.intelligence": "విశ్లేషణ", "nav.trust": "పారదర్శకత",
    "nav.overview": "సమగ్ర దృశ్యం", "nav.worklist": "విచారణ జాబితా", "nav.trends": "కాల ధోరణి",
    "nav.duplicates": "సారూప్య పనులు", "nav.compliance": "అనుసరణ",
    "nav.archetypes": "పని రకాలు", "nav.transparency": "డేటా పారదర్శకత",
    "nav.how": "ఇది ఎలా పనిచేస్తుంది",
    "shell.brandSub": "ఫోరెన్సిక్ పర్యవేక్షణ", "shell.stakeholder": "వినియోగదారు దృక్కోణం",
    "shell.roleSim": "పాత్ర అనుకరణ — ఈ నమూనాలో ప్రామాణీకరణ లేదు",
    "shell.viewingAs": "చూస్తున్నారు", "shell.chain": "నేర్చుకో, పోల్చు, అంచనా వేయి, వివరించు, ప్రాధాన్యత ఇవ్వు",
    "shell.leadsNotVerdicts": "విచారణ సూచనలు, తీర్పులు కావు. ప్రతి చర్యను మనిషే నిర్ణయిస్తారు.",
    "overview.title": "జాతీయ సమగ్ర దృశ్యం", "overview.worksMonitored": "పర్యవేక్షణలోని పనులు",
    "overview.totalRecommended": "మొత్తం సిఫార్సు మొత్తం", "overview.exposure": "ప్రమాదంలో ఉన్న మొత్తం",
    "overview.exposureFoot": "పూర్తి-ప్రమాద ఆధారంగా — నష్టం కాదు, ఖర్చు కాదు",
    "overview.leads": "విచారణ సూచనలు", "overview.byState": "రాష్ట్రాలవారీ ప్రమాద మొత్తం (టాప్ 10, కోట్లు)",
    "overview.bands": "విశ్వాస స్థాయిలు", "overview.archetypes": "గుర్తించిన పని రకాలు",
    "overview.completed": "పూర్తయినవి", "overview.open": "కొనసాగుతున్నవి",
    "worklist.title": "విచారణ జాబితా",
    "worklist.sub": "ఆడిట్-లాభం ఆధారంగా వరుస — ప్రాధాన్యత × ప్రమాద మొత్తం × ధృవీకరణ",
    "worklist.search": "వివరణ లేదా అమలు సంస్థను వెతకండి", "worklist.allStates": "అన్ని రాష్ట్రాలు",
    "worklist.allBands": "అన్ని స్థాయిలు", "worklist.empty": "ఈ ఫిల్టర్లకు ఫలితాలు లేవు.",
    "worklist.work": "పని", "worklist.state": "రాష్ట్రం", "worklist.confidence": "విశ్వాసం",
    "worklist.amount": "మొత్తం", "worklist.auditRoi": "ఆడిట్-లాభం", "worklist.prev": "మునుపటి",
    "worklist.next": "తదుపరి", "worklist.page": "పేజీ", "worklist.of": "లో",
    "case.title": "కేసు ఫైల్", "case.back": "జాబితాకు తిరిగి",
    "case.evidence": "సాక్ష్యం — ఇది ఎందుకు వచ్చింది", "case.peerContext": "సమాన పోలిక",
    "case.nextStep": "సిఫార్సు చేసిన తదుపరి అడుగు", "case.recommended": "సిఫార్సు చేయబడింది",
    "case.completionRisk": "పూర్తి ప్రమాదం", "case.corroboration": "ధృవీకరణ",
    "case.families": "వర్గాలు", "case.earlyWarning": "ముందస్తు హెచ్చరిక",
    "case.compliance": "అనుసరణ ఫలితాలు", "case.duplicate": "సారూప్య పని అవకాశం",
    "case.aiBrief": "AI సారాంశం", "case.archetype": "పని రకం",
    "case.peerLevel": "పోలిక స్థాయి", "case.peerSize": "సమాన సమూహ పరిమాణం",
    "case.amountPercentile": "మొత్తం శాతం",
    "banner.hitl": "ఇవి విచారణ సూచనలు, తీర్పులు కావు. ప్రతి అంశం పారదర్శక, పరస్పరం ధృవీకరించిన "
                   "సంకేతాల ఆధారంగా ఆడిట్-లాభం ప్రకారం వరుసలో ఉంది. ఈ డేటాలో దోష జాబితా లేదు — "
                   "సాక్ష్యాన్ని చూసి మనిషే నిర్ణయిస్తారు.",
    "common.loading": "సమాచారం లోడ్ అవుతోంది", "common.works": "పనులు", "common.leads": "సూచనలు",
    "common.language": "భాష", "common.generating": "సారాంశం సిద్ధమవుతోంది",
}

MR: dict[str, str] = {
    "nav.monitor": "देखरेख", "nav.intelligence": "विश्लेषण", "nav.trust": "पारदर्शकता",
    "nav.overview": "एकूण चित्र", "nav.worklist": "तपास यादी", "nav.trends": "कालानुरूप कल",
    "nav.duplicates": "समान कामे", "nav.compliance": "अनुपालन", "nav.archetypes": "कामाचे प्रकार",
    "nav.transparency": "डेटा पारदर्शकता", "nav.how": "हे कसे कार्य करते",
    "shell.brandSub": "न्यायवैद्यक देखरेख", "shell.stakeholder": "वापरकर्ता दृष्टिकोन",
    "shell.roleSim": "भूमिका अनुकरण — या नमुन्यात प्रमाणीकरण नाही",
    "shell.viewingAs": "पाहत आहात", "shell.chain": "शिका, तुलना करा, अंदाज लावा, स्पष्ट करा, प्राधान्य द्या",
    "shell.leadsNotVerdicts": "तपासाचे संकेत, निर्णय नाहीत. प्रत्येक कृती माणूसच ठरवतो.",
    "overview.title": "राष्ट्रीय एकूण चित्र", "overview.worksMonitored": "देखरेखीखालील कामे",
    "overview.totalRecommended": "एकूण शिफारस रक्कम", "overview.exposure": "धोक्यातील रक्कम",
    "overview.exposureFoot": "पूर्तता-जोखीम आधारित — तोटा नाही, खर्च नाही",
    "overview.leads": "तपासाचे संकेत", "overview.byState": "राज्यनिहाय धोका (शीर्ष 10, कोटी)",
    "overview.bands": "विश्वास पातळी", "overview.archetypes": "ओळखलेले कामाचे प्रकार",
    "overview.completed": "पूर्ण", "overview.open": "सुरू",
    "worklist.title": "तपास यादी",
    "worklist.sub": "ऑडिट-लाभानुसार क्रम — प्राधान्य × धोका रक्कम × पुष्टी",
    "worklist.search": "वर्णन किंवा अंमलबजावणी संस्था शोधा", "worklist.allStates": "सर्व राज्ये",
    "worklist.allBands": "सर्व पातळ्या", "worklist.empty": "या फिल्टरसाठी निकाल नाहीत.",
    "worklist.work": "काम", "worklist.state": "राज्य", "worklist.confidence": "विश्वास",
    "worklist.amount": "रक्कम", "worklist.auditRoi": "ऑडिट-लाभ", "worklist.prev": "मागील",
    "worklist.next": "पुढील", "worklist.page": "पृष्ठ", "worklist.of": "पैकी",
    "case.title": "प्रकरण फाइल", "case.back": "यादीकडे परत",
    "case.evidence": "पुरावा — हे का समोर आले", "case.peerContext": "समकक्ष तुलना",
    "case.nextStep": "शिफारस केलेले पुढील पाऊल", "case.recommended": "शिफारस केलेले",
    "case.completionRisk": "पूर्तता जोखीम", "case.corroboration": "पुष्टी",
    "case.families": "श्रेणी", "case.earlyWarning": "पूर्वसूचना",
    "case.compliance": "अनुपालन निष्कर्ष", "case.duplicate": "संभाव्य समान काम",
    "case.aiBrief": "एआय सारांश", "case.archetype": "कामाचा प्रकार",
    "case.peerLevel": "तुलना पातळी", "case.peerSize": "समकक्ष गटाचा आकार",
    "case.amountPercentile": "रक्कम शतमान",
    "banner.hitl": "हे तपासाचे संकेत आहेत, निर्णय नाहीत. प्रत्येक बाब पारदर्शक व परस्पर पुष्ट "
                   "संकेतांच्या आधारे ऑडिट-लाभानुसार क्रमवारीत आहे. या डेटात दोषसूची नाही — "
                   "पुरावा पाहून माणूसच निर्णय घेतो.",
    "common.loading": "माहिती लोड होत आहे", "common.works": "कामे", "common.leads": "संकेत",
    "common.language": "भाषा", "common.generating": "सारांश तयार होत आहे",
}

GU: dict[str, str] = {
    "nav.monitor": "દેખરેખ", "nav.intelligence": "વિશ્લેષણ", "nav.trust": "પારદર્શિતા",
    "nav.overview": "સમગ્ર ચિત્ર", "nav.worklist": "તપાસ યાદી", "nav.trends": "સમય વલણ",
    "nav.duplicates": "સમાન કામો", "nav.compliance": "અનુપાલન", "nav.archetypes": "કામના પ્રકાર",
    "nav.transparency": "ડેટા પારદર્શિતા", "nav.how": "આ કેવી રીતે કામ કરે છે",
    "shell.brandSub": "ફોરેન્સિક દેખરેખ", "shell.stakeholder": "વપરાશકર્તા દૃષ્ટિકોણ",
    "shell.roleSim": "ભૂમિકા અનુકરણ — આ પ્રોટોટાઇપમાં પ્રમાણીકરણ નથી",
    "shell.viewingAs": "જોઈ રહ્યા છો", "shell.chain": "શીખો, સરખાવો, અનુમાન કરો, સમજાવો, પ્રાથમિકતા આપો",
    "shell.leadsNotVerdicts": "તપાસના સંકેત, ચુકાદા નહીં. દરેક પગલું માણસ જ નક્કી કરે છે.",
    "overview.title": "રાષ્ટ્રીય સમગ્ર ચિત્ર", "overview.worksMonitored": "દેખરેખ હેઠળના કામો",
    "overview.totalRecommended": "કુલ ભલામણ રકમ", "overview.exposure": "જોખમમાં રકમ",
    "overview.exposureFoot": "પૂર્ણતા-જોખમ આધારિત — નુકસાન નહીં, ખર્ચ નહીં",
    "overview.leads": "તપાસના સંકેત", "overview.byState": "રાજ્યવાર જોખમ (ટોચના 10, કરોડ)",
    "overview.bands": "વિશ્વાસ સ્તર", "overview.archetypes": "ઓળખાયેલા કામના પ્રકાર",
    "overview.completed": "પૂર્ણ", "overview.open": "ચાલુ",
    "worklist.title": "તપાસ યાદી",
    "worklist.sub": "ઓડિટ-લાભ મુજબ ક્રમ — પ્રાથમિકતા × જોખમ રકમ × સમર્થન",
    "worklist.search": "વર્ણન અથવા અમલીકરણ સંસ્થા શોધો", "worklist.allStates": "બધા રાજ્યો",
    "worklist.allBands": "બધા સ્તર", "worklist.empty": "આ ફિલ્ટર માટે કોઈ પરિણામ નથી.",
    "worklist.work": "કામ", "worklist.state": "રાજ્ય", "worklist.confidence": "વિશ્વાસ",
    "worklist.amount": "રકમ", "worklist.auditRoi": "ઓડિટ-લાભ", "worklist.prev": "પાછલું",
    "worklist.next": "આગળનું", "worklist.page": "પૃષ્ઠ", "worklist.of": "માંથી",
    "case.title": "કેસ ફાઇલ", "case.back": "યાદી પર પાછા",
    "case.evidence": "પુરાવો — આ કેમ સામે આવ્યું", "case.peerContext": "સમકક્ષ સરખામણી",
    "case.nextStep": "ભલામણ કરેલ આગળનું પગલું", "case.recommended": "ભલામણ કરેલ",
    "case.completionRisk": "પૂર્ણતા જોખમ", "case.corroboration": "સમર્થન",
    "case.families": "શ્રેણીઓ", "case.earlyWarning": "પૂર્વ ચેતવણી",
    "case.compliance": "અનુપાલન તારણો", "case.duplicate": "સંભવિત સમાન કામ",
    "case.aiBrief": "AI સારાંશ", "case.archetype": "કામનો પ્રકાર",
    "case.peerLevel": "સરખામણી સ્તર", "case.peerSize": "સમકક્ષ જૂથનું કદ",
    "case.amountPercentile": "રકમ ટકાવારી",
    "banner.hitl": "આ તપાસના સંકેત છે, ચુકાદા નહીં. દરેક બાબત પારદર્શક અને પરસ્પર સમર્થિત "
                   "સંકેતોના આધારે ઓડિટ-લાભ મુજબ ક્રમમાં છે. આ ડેટામાં દોષ-યાદી નથી — "
                   "પુરાવો જોઈને માણસ જ નિર્ણય લે છે.",
    "common.loading": "માહિતી લોડ થઈ રહી છે", "common.works": "કામો", "common.leads": "સંકેત",
    "common.language": "ભાષા", "common.generating": "સારાંશ તૈયાર થઈ રહ્યો છે",
}

KN: dict[str, str] = {
    "nav.monitor": "ಮೇಲ್ವಿಚಾರಣೆ", "nav.intelligence": "ವಿಶ್ಲೇಷಣೆ", "nav.trust": "ಪಾರದರ್ಶಕತೆ",
    "nav.overview": "ಸಮಗ್ರ ನೋಟ", "nav.worklist": "ತನಿಖೆ ಪಟ್ಟಿ", "nav.trends": "ಕಾಲಿಕ ಪ್ರವೃತ್ತಿ",
    "nav.duplicates": "ಸಮಾನ ಕಾಮಗಾರಿಗಳು", "nav.compliance": "ಅನುಸರಣೆ",
    "nav.archetypes": "ಕಾಮಗಾರಿ ಪ್ರಕಾರಗಳು", "nav.transparency": "ದತ್ತಾಂಶ ಪಾರದರ್ಶಕತೆ",
    "nav.how": "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",
    "shell.brandSub": "ವಿಧಿವಿಜ್ಞಾನ ಮೇಲ್ವಿಚಾರಣೆ", "shell.stakeholder": "ಬಳಕೆದಾರ ದೃಷ್ಟಿಕೋನ",
    "shell.roleSim": "ಪಾತ್ರ ಅನುಕರಣೆ — ಈ ಮಾದರಿಯಲ್ಲಿ ದೃಢೀಕರಣವಿಲ್ಲ",
    "shell.viewingAs": "ನೋಡುತ್ತಿದ್ದೀರಿ", "shell.chain": "ಕಲಿಯಿರಿ, ಹೋಲಿಸಿ, ಊಹಿಸಿ, ವಿವರಿಸಿ, ಆದ್ಯತೆ ನೀಡಿ",
    "shell.leadsNotVerdicts": "ತನಿಖೆಯ ಸೂಚನೆಗಳು, ತೀರ್ಪುಗಳಲ್ಲ. ಪ್ರತಿ ಕ್ರಮವನ್ನೂ ಮನುಷ್ಯನೇ ನಿರ್ಧರಿಸುತ್ತಾನೆ.",
    "overview.title": "ರಾಷ್ಟ್ರೀಯ ಸಮಗ್ರ ನೋಟ", "overview.worksMonitored": "ಮೇಲ್ವಿಚಾರಣೆಯಲ್ಲಿರುವ ಕಾಮಗಾರಿಗಳು",
    "overview.totalRecommended": "ಒಟ್ಟು ಶಿಫಾರಸು ಮೊತ್ತ", "overview.exposure": "ಅಪಾಯದಲ್ಲಿರುವ ಮೊತ್ತ",
    "overview.exposureFoot": "ಪೂರ್ಣಗೊಳ್ಳುವ-ಅಪಾಯ ಆಧರಿತ — ನಷ್ಟವಲ್ಲ, ವೆಚ್ಚವಲ್ಲ",
    "overview.leads": "ತನಿಖೆಯ ಸೂಚನೆಗಳು", "overview.byState": "ರಾಜ್ಯವಾರು ಅಪಾಯ (ಮೊದಲ 10, ಕೋಟಿ)",
    "overview.bands": "ವಿಶ್ವಾಸ ಮಟ್ಟಗಳು", "overview.archetypes": "ಗುರುತಿಸಿದ ಕಾಮಗಾರಿ ಪ್ರಕಾರಗಳು",
    "overview.completed": "ಪೂರ್ಣ", "overview.open": "ಪ್ರಗತಿಯಲ್ಲಿ",
    "worklist.title": "ತನಿಖೆ ಪಟ್ಟಿ",
    "worklist.sub": "ಲೆಕ್ಕಪರಿಶೋಧನಾ-ಲಾಭದ ಪ್ರಕಾರ ಕ್ರಮ — ಆದ್ಯತೆ × ಅಪಾಯ ಮೊತ್ತ × ದೃಢೀಕರಣ",
    "worklist.search": "ವಿವರಣೆ ಅಥವಾ ಅನುಷ್ಠಾನ ಸಂಸ್ಥೆಯನ್ನು ಹುಡುಕಿ", "worklist.allStates": "ಎಲ್ಲಾ ರಾಜ್ಯಗಳು",
    "worklist.allBands": "ಎಲ್ಲಾ ಮಟ್ಟಗಳು", "worklist.empty": "ಈ ಫಿಲ್ಟರ್‌ಗಳಿಗೆ ಫಲಿತಾಂಶವಿಲ್ಲ.",
    "worklist.work": "ಕಾಮಗಾರಿ", "worklist.state": "ರಾಜ್ಯ", "worklist.confidence": "ವಿಶ್ವಾಸ",
    "worklist.amount": "ಮೊತ್ತ", "worklist.auditRoi": "ಲೆಕ್ಕಪರಿಶೋಧನಾ-ಲಾಭ", "worklist.prev": "ಹಿಂದಿನದು",
    "worklist.next": "ಮುಂದಿನದು", "worklist.page": "ಪುಟ", "worklist.of": "ರಲ್ಲಿ",
    "case.title": "ಪ್ರಕರಣ ಕಡತ", "case.back": "ಪಟ್ಟಿಗೆ ಹಿಂತಿರುಗಿ",
    "case.evidence": "ಸಾಕ್ಷ್ಯ — ಇದು ಏಕೆ ಬಂದಿತು", "case.peerContext": "ಸಮಾನ ಹೋಲಿಕೆ",
    "case.nextStep": "ಶಿಫಾರಸು ಮಾಡಿದ ಮುಂದಿನ ಹೆಜ್ಜೆ", "case.recommended": "ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ",
    "case.completionRisk": "ಪೂರ್ಣಗೊಳ್ಳುವ ಅಪಾಯ", "case.corroboration": "ದೃಢೀಕರಣ",
    "case.families": "ವರ್ಗಗಳು", "case.earlyWarning": "ಮುನ್ನೆಚ್ಚರಿಕೆ",
    "case.compliance": "ಅನುಸರಣೆ ಸಂಶೋಧನೆಗಳು", "case.duplicate": "ಸಂಭಾವ್ಯ ಸಮಾನ ಕಾಮಗಾರಿ",
    "case.aiBrief": "AI ಸಾರಾಂಶ", "case.archetype": "ಕಾಮಗಾರಿ ಪ್ರಕಾರ",
    "case.peerLevel": "ಹೋಲಿಕೆ ಮಟ್ಟ", "case.peerSize": "ಸಮಾನ ಗುಂಪಿನ ಗಾತ್ರ",
    "case.amountPercentile": "ಮೊತ್ತ ಶೇಕಡಾವಾರು",
    "banner.hitl": "ಇವು ತನಿಖೆಯ ಸೂಚನೆಗಳು, ತೀರ್ಪುಗಳಲ್ಲ. ಪ್ರತಿ ಅಂಶವೂ ಪಾರದರ್ಶಕ ಮತ್ತು ಪರಸ್ಪರ "
                   "ದೃಢೀಕೃತ ಸಂಕೇತಗಳ ಆಧಾರದ ಮೇಲೆ ಕ್ರಮದಲ್ಲಿದೆ. ಈ ದತ್ತಾಂಶದಲ್ಲಿ ದೋಷ ಪಟ್ಟಿ ಇಲ್ಲ — "
                   "ಸಾಕ್ಷ್ಯ ನೋಡಿ ಮನುಷ್ಯನೇ ನಿರ್ಧರಿಸುತ್ತಾನೆ.",
    "common.loading": "ಮಾಹಿತಿ ಲೋಡ್ ಆಗುತ್ತಿದೆ", "common.works": "ಕಾಮಗಾರಿಗಳು", "common.leads": "ಸೂಚನೆಗಳು",
    "common.language": "ಭಾಷೆ", "common.generating": "ಸಾರಾಂಶ ಸಿದ್ಧವಾಗುತ್ತಿದೆ",
}

ML: dict[str, str] = {
    "nav.monitor": "നിരീക്ഷണം", "nav.intelligence": "വിശകലനം", "nav.trust": "സുതാര്യത",
    "nav.overview": "സമഗ്ര ചിത്രം", "nav.worklist": "അന്വേഷണ പട്ടിക", "nav.trends": "കാല പ്രവണത",
    "nav.duplicates": "സമാന പ്രവൃത്തികൾ", "nav.compliance": "അനുസരണം",
    "nav.archetypes": "പ്രവൃത്തി വിഭാഗങ്ങൾ", "nav.transparency": "ഡാറ്റ സുതാര്യത",
    "nav.how": "ഇത് എങ്ങനെ പ്രവർത്തിക്കുന്നു",
    "shell.brandSub": "ഫോറൻസിക് നിരീക്ഷണം", "shell.stakeholder": "ഉപയോക്തൃ കാഴ്ചപ്പാട്",
    "shell.roleSim": "റോൾ അനുകരണം — ഈ മാതൃകയിൽ ആധികാരികത ഇല്ല",
    "shell.viewingAs": "കാണുന്നത്", "shell.chain": "പഠിക്കുക, താരതമ്യം ചെയ്യുക, പ്രവചിക്കുക, വിശദീകരിക്കുക, മുൻഗണന നൽകുക",
    "shell.leadsNotVerdicts": "അന്വേഷണ സൂചനകൾ, വിധികളല്ല. ഓരോ നടപടിയും മനുഷ്യൻ തീരുമാനിക്കുന്നു.",
    "overview.title": "ദേശീയ സമഗ്ര ചിത്രം", "overview.worksMonitored": "നിരീക്ഷണത്തിലുള്ള പ്രവൃത്തികൾ",
    "overview.totalRecommended": "ആകെ ശുപാർശ തുക", "overview.exposure": "അപകടസാധ്യതയിലുള്ള തുക",
    "overview.exposureFoot": "പൂർത്തീകരണ-സാധ്യത അടിസ്ഥാനത്തിൽ — നഷ്ടമല്ല, ചെലവല്ല",
    "overview.leads": "അന്വേഷണ സൂചനകൾ", "overview.byState": "സംസ്ഥാനതലത്തിൽ അപകടസാധ്യത (ആദ്യ 10, കോടി)",
    "overview.bands": "വിശ്വാസ നിലകൾ", "overview.archetypes": "കണ്ടെത്തിയ പ്രവൃത്തി വിഭാഗങ്ങൾ",
    "overview.completed": "പൂർത്തിയായി", "overview.open": "നടക്കുന്നു",
    "worklist.title": "അന്വേഷണ പട്ടിക",
    "worklist.sub": "ഓഡിറ്റ്-ലാഭം അനുസരിച്ച് ക്രമം — മുൻഗണന × അപകട തുക × സ്ഥിരീകരണം",
    "worklist.search": "വിവരണം അല്ലെങ്കിൽ നിർവഹണ ഏജൻസി തിരയുക", "worklist.allStates": "എല്ലാ സംസ്ഥാനങ്ങളും",
    "worklist.allBands": "എല്ലാ നിലകളും", "worklist.empty": "ഈ ഫിൽട്ടറുകൾക്ക് ഫലങ്ങളില്ല.",
    "worklist.work": "പ്രവൃത്തി", "worklist.state": "സംസ്ഥാനം", "worklist.confidence": "വിശ്വാസം",
    "worklist.amount": "തുക", "worklist.auditRoi": "ഓഡിറ്റ്-ലാഭം", "worklist.prev": "മുമ്പത്തേത്",
    "worklist.next": "അടുത്തത്", "worklist.page": "പേജ്", "worklist.of": "ൽ",
    "case.title": "കേസ് ഫയൽ", "case.back": "പട്ടികയിലേക്ക് മടങ്ങുക",
    "case.evidence": "തെളിവ് — ഇത് എന്തുകൊണ്ട് വന്നു", "case.peerContext": "സമാന താരതമ്യം",
    "case.nextStep": "ശുപാർശ ചെയ്ത അടുത്ത നടപടി", "case.recommended": "ശുപാർശ ചെയ്തത്",
    "case.completionRisk": "പൂർത്തീകരണ സാധ്യത", "case.corroboration": "സ്ഥിരീകരണം",
    "case.families": "വിഭാഗങ്ങൾ", "case.earlyWarning": "മുൻകൂർ മുന്നറിയിപ്പ്",
    "case.compliance": "അനുസരണ കണ്ടെത്തലുകൾ", "case.duplicate": "സാധ്യമായ സമാന പ്രവൃത്തി",
    "case.aiBrief": "AI സംഗ്രഹം", "case.archetype": "പ്രവൃത്തി വിഭാഗം",
    "case.peerLevel": "താരതമ്യ നില", "case.peerSize": "സമാന ഗ്രൂപ്പിന്റെ വലുപ്പം",
    "case.amountPercentile": "തുക ശതമാനം",
    "banner.hitl": "ഇവ അന്വേഷണ സൂചനകളാണ്, വിധികളല്ല. ഓരോ ഇനവും സുതാര്യവും പരസ്പരം "
                   "സ്ഥിരീകരിച്ചതുമായ സൂചനകളുടെ അടിസ്ഥാനത്തിൽ ക്രമീകരിച്ചിരിക്കുന്നു. ഈ ഡാറ്റയിൽ "
                   "കുറ്റപ്പട്ടികയില്ല — തെളിവ് കണ്ട് മനുഷ്യനാണ് തീരുമാനിക്കുന്നത്.",
    "common.loading": "വിവരങ്ങൾ ലോഡ് ചെയ്യുന്നു", "common.works": "പ്രവൃത്തികൾ", "common.leads": "സൂചനകൾ",
    "common.language": "ഭാഷ", "common.generating": "സംഗ്രഹം തയ്യാറാകുന്നു",
}

PA: dict[str, str] = {
    "nav.monitor": "ਨਿਗਰਾਨੀ", "nav.intelligence": "ਵਿਸ਼ਲੇਸ਼ਣ", "nav.trust": "ਪਾਰਦਰਸ਼ਤਾ",
    "nav.overview": "ਸਮੁੱਚੀ ਤਸਵੀਰ", "nav.worklist": "ਜਾਂਚ ਸੂਚੀ", "nav.trends": "ਸਮੇਂ ਦਾ ਰੁਝਾਨ",
    "nav.duplicates": "ਸਮਾਨ ਕੰਮ", "nav.compliance": "ਪਾਲਣਾ", "nav.archetypes": "ਕੰਮ ਦੀਆਂ ਕਿਸਮਾਂ",
    "nav.transparency": "ਡੇਟਾ ਪਾਰਦਰਸ਼ਤਾ", "nav.how": "ਇਹ ਕਿਵੇਂ ਕੰਮ ਕਰਦਾ ਹੈ",
    "shell.brandSub": "ਫੋਰੈਂਸਿਕ ਨਿਗਰਾਨੀ", "shell.stakeholder": "ਵਰਤੋਂਕਾਰ ਦ੍ਰਿਸ਼ਟੀਕੋਣ",
    "shell.roleSim": "ਭੂਮਿਕਾ ਨਕਲ — ਇਸ ਨਮੂਨੇ ਵਿੱਚ ਪ੍ਰਮਾਣਿਕਤਾ ਨਹੀਂ ਹੈ",
    "shell.viewingAs": "ਵੇਖ ਰਹੇ ਹੋ", "shell.chain": "ਸਿੱਖੋ, ਤੁਲਨਾ ਕਰੋ, ਅਨੁਮਾਨ ਲਗਾਓ, ਸਮਝਾਓ, ਤਰਜੀਹ ਦਿਓ",
    "shell.leadsNotVerdicts": "ਜਾਂਚ ਦੇ ਸੰਕੇਤ, ਫੈਸਲੇ ਨਹੀਂ। ਹਰ ਕਾਰਵਾਈ ਮਨੁੱਖ ਹੀ ਤੈਅ ਕਰਦਾ ਹੈ।",
    "overview.title": "ਰਾਸ਼ਟਰੀ ਸਮੁੱਚੀ ਤਸਵੀਰ", "overview.worksMonitored": "ਨਿਗਰਾਨੀ ਹੇਠ ਕੰਮ",
    "overview.totalRecommended": "ਕੁੱਲ ਸਿਫ਼ਾਰਸ਼ ਰਕਮ", "overview.exposure": "ਜੋਖਮ ਵਿੱਚ ਰਕਮ",
    "overview.exposureFoot": "ਪੂਰਤੀ-ਜੋਖਮ ਅਧਾਰਿਤ — ਨੁਕਸਾਨ ਨਹੀਂ, ਖਰਚ ਨਹੀਂ",
    "overview.leads": "ਜਾਂਚ ਦੇ ਸੰਕੇਤ", "overview.byState": "ਰਾਜ ਅਨੁਸਾਰ ਜੋਖਮ (ਪਹਿਲੇ 10, ਕਰੋੜ)",
    "overview.bands": "ਭਰੋਸੇ ਦੇ ਪੱਧਰ", "overview.archetypes": "ਪਛਾਣੀਆਂ ਕੰਮ ਕਿਸਮਾਂ",
    "overview.completed": "ਮੁਕੰਮਲ", "overview.open": "ਜਾਰੀ",
    "worklist.title": "ਜਾਂਚ ਸੂਚੀ",
    "worklist.sub": "ਆਡਿਟ-ਲਾਭ ਅਨੁਸਾਰ ਕ੍ਰਮ — ਤਰਜੀਹ × ਜੋਖਮ ਰਕਮ × ਪੁਸ਼ਟੀ",
    "worklist.search": "ਵੇਰਵਾ ਜਾਂ ਲਾਗੂਕਰਨ ਏਜੰਸੀ ਖੋਜੋ", "worklist.allStates": "ਸਾਰੇ ਰਾਜ",
    "worklist.allBands": "ਸਾਰੇ ਪੱਧਰ", "worklist.empty": "ਇਹਨਾਂ ਫਿਲਟਰਾਂ ਲਈ ਕੋਈ ਨਤੀਜਾ ਨਹੀਂ।",
    "worklist.work": "ਕੰਮ", "worklist.state": "ਰਾਜ", "worklist.confidence": "ਭਰੋਸਾ",
    "worklist.amount": "ਰਕਮ", "worklist.auditRoi": "ਆਡਿਟ-ਲਾਭ", "worklist.prev": "ਪਿਛਲਾ",
    "worklist.next": "ਅਗਲਾ", "worklist.page": "ਸਫ਼ਾ", "worklist.of": "ਵਿੱਚੋਂ",
    "case.title": "ਕੇਸ ਫਾਈਲ", "case.back": "ਸੂਚੀ ਤੇ ਵਾਪਸ",
    "case.evidence": "ਸਬੂਤ — ਇਹ ਕਿਉਂ ਸਾਹਮਣੇ ਆਇਆ", "case.peerContext": "ਸਮਕਕਸ਼ ਤੁਲਨਾ",
    "case.nextStep": "ਸਿਫ਼ਾਰਸ਼ ਕੀਤਾ ਅਗਲਾ ਕਦਮ", "case.recommended": "ਸਿਫ਼ਾਰਸ਼ ਕੀਤਾ",
    "case.completionRisk": "ਪੂਰਤੀ ਜੋਖਮ", "case.corroboration": "ਪੁਸ਼ਟੀ",
    "case.families": "ਸ਼੍ਰੇਣੀਆਂ", "case.earlyWarning": "ਪਹਿਲੀ ਚੇਤਾਵਨੀ",
    "case.compliance": "ਪਾਲਣਾ ਨਤੀਜੇ", "case.duplicate": "ਸੰਭਾਵਿਤ ਸਮਾਨ ਕੰਮ",
    "case.aiBrief": "AI ਸਾਰ", "case.archetype": "ਕੰਮ ਦੀ ਕਿਸਮ",
    "case.peerLevel": "ਤੁਲਨਾ ਪੱਧਰ", "case.peerSize": "ਸਮਕਕਸ਼ ਸਮੂਹ ਦਾ ਆਕਾਰ",
    "case.amountPercentile": "ਰਕਮ ਪ੍ਰਤੀਸ਼ਤ",
    "banner.hitl": "ਇਹ ਜਾਂਚ ਦੇ ਸੰਕੇਤ ਹਨ, ਫੈਸਲੇ ਨਹੀਂ। ਹਰ ਮਦ ਪਾਰਦਰਸ਼ੀ ਅਤੇ ਆਪਸੀ ਪੁਸ਼ਟ ਸੰਕੇਤਾਂ "
                   "ਦੇ ਆਧਾਰ ਤੇ ਕ੍ਰਮਬੱਧ ਹੈ। ਇਸ ਡੇਟਾ ਵਿੱਚ ਕੋਈ ਦੋਸ਼-ਸੂਚੀ ਨਹੀਂ — ਸਬੂਤ ਵੇਖ ਕੇ "
                   "ਮਨੁੱਖ ਹੀ ਫੈਸਲਾ ਕਰਦਾ ਹੈ।",
    "common.loading": "ਜਾਣਕਾਰੀ ਲੋਡ ਹੋ ਰਹੀ ਹੈ", "common.works": "ਕੰਮ", "common.leads": "ਸੰਕੇਤ",
    "common.language": "ਭਾਸ਼ਾ", "common.generating": "ਸਾਰ ਤਿਆਰ ਹੋ ਰਿਹਾ ਹੈ",
}

#: language code -> (English name, native name, bundle)
BUNDLES: dict[str, tuple[str, str, dict[str, str]]] = {
    "en": ("English", "English", UI),
    "hi": ("Hindi", "हिन्दी", HI),
    "bn": ("Bengali", "বাংলা", BN),
    "ta": ("Tamil", "தமிழ்", TA),
    "te": ("Telugu", "తెలుగు", TE),
    "mr": ("Marathi", "मराठी", MR),
    "gu": ("Gujarati", "ગુજરાતી", GU),
    "kn": ("Kannada", "ಕನ್ನಡ", KN),
    "ml": ("Malayalam", "മലയാളം", ML),
    "pa": ("Punjabi", "ਪੰਜਾਬੀ", PA),
}


def bundle(language: str) -> dict[str, str]:
    """The complete bundle for a language, English-filled for any key not translated."""
    entry = BUNDLES.get(language)
    if entry is None:
        return dict(UI)
    return {key: entry[2].get(key, english) for key, english in UI.items()}


def coverage(language: str) -> float:
    """Share of UI keys with a real translation. Used by tests, not guessed at."""
    entry = BUNDLES.get(language)
    if entry is None or language == "en":
        return 1.0
    return sum(1 for key in UI if key in entry[2]) / len(UI)
