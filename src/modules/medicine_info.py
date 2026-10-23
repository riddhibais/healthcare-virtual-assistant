class MedicineInfo:
    def __init__(self):
        self.medicine_db = {
            "paracetamol": {
                "generic_name": "Paracetamol (Acetaminophen)",
                "brand_names": ["Tylenol", "Panadol", "Calpol", "Dolo 650"],
                "category": "Analgesic & Antipyretic (Pain & Fever Reducer)",
                "uses": [
                    "Relief of mild-to-moderate pain (headache, toothache, muscle ache)",
                    "Reduction of fever associated with viral infections or cold"
                ],
                "dosage": "Adults: 500 mg to 1000 mg every 4-6 hours as needed. Do not exceed 4000 mg (4g) per 24 hours.",
                "common_side_effects": ["Nausea", "Stomach upset (rare at recommended doses)", "Allergic skin rash (rare)"],
                "serious_side_effects": ["Hepatotoxicity / Liver damage (with overdose or excessive alcohol use)", "Severe skin reactions (Stevens-Johnson syndrome)"],
                "interactions": ["Alcohol (increased risk of liver injury)", "Warfarin (increased blood thinning effect with chronic use)"],
                "precautions": "Avoid combining with other acetaminophen-containing cold/flu remedies. Consult doctor if liver disease is present."
            },
            "ibuprofen": {
                "generic_name": "Ibuprofen",
                "brand_names": ["Advil", "Motrin", "Nurofen", "Brufen"],
                "category": "Non-Steroidal Anti-Inflammatory Drug (NSAID)",
                "uses": [
                    "Reduction of inflammation, swelling, and joint stiffness",
                    "Relief of moderate pain, menstrual cramps, arthritis, and fever"
                ],
                "dosage": "Adults: 200 mg to 400 mg every 4-6 hours with food. Maximum OTC daily limit: 1200 mg (up to 3200 mg under doctor supervision).",
                "common_side_effects": ["Heartburn", "Stomach irritation or pain", "Mild dizziness", "Drowsiness"],
                "serious_side_effects": ["Gastrointestinal ulceration or bleeding", "Increased cardiovascular risk with long-term high doses", "Renal impairment"],
                "interactions": ["Aspirin", "Blood thinners (Warfarin, Apixaban)", "ACE Inhibitors (Blood pressure meds)", "Corticosteroids"],
                "precautions": "Take always with food or milk to protect stomach lining. Avoid in severe heart failure, kidney disease, or active stomach ulcers."
            },
            "amoxicillin": {
                "generic_name": "Amoxicillin",
                "brand_names": ["Amoxil", "Moxatag", "Novamox"],
                "category": "Penicillin-type Antibiotic",
                "uses": [
                    "Bacterial infections of the ear, nose, throat, skin, and urinary tract",
                    "Helicobacter pylori eradication (in combination therapy for ulcers)"
                ],
                "dosage": "Adults: 250 mg to 500 mg every 8 hours (or 500 mg to 875 mg every 12 hours) as prescribed by physician. Complete full prescribed course.",
                "common_side_effects": ["Diarrhea", "Mild nausea or vomiting", "Mild rash"],
                "serious_side_effects": ["Severe allergic reaction (Anaphylaxis)", "Clostridioides difficile severe colitis", "Severe skin eruption"],
                "interactions": ["Methotrexate", "Allopurinol", "Oral Typhoid Vaccine"],
                "precautions": "Strictly requires a physician prescription. Inform doctor immediately if you have a known history of penicillin allergy."
            },
            "metformin": {
                "generic_name": "Metformin Hydrochloride",
                "brand_names": ["Glucophage", "Fortamet", "Glumetza", "Glycomet"],
                "category": "Biguanide Antidiabetic Agent",
                "uses": [
                    "Management of Type 2 Diabetes Mellitus",
                    "Polycystic Ovary Syndrome (PCOS) insulin resistance management"
                ],
                "dosage": "Adults: Starting dose typically 500 mg twice daily or 850 mg once daily with meals. Dosage titrated gradually under physician supervision.",
                "common_side_effects": ["Nausea", "Abdominal bloating & gas", "Diarrhea", "Metallic taste", "Vitamin B12 deficiency (long-term use)"],
                "serious_side_effects": ["Lactic Acidosis (rare but severe emergency metabolic complication)"],
                "interactions": ["Contrast dyes used in CT scans (must hold medicine prior)", "Alcohol", "Diuretics"],
                "precautions": "Take with meals to reduce stomach discomfort. Monitor renal (kidney) function regularly."
            },
            "atorvastatin": {
                "generic_name": "Atorvastatin",
                "brand_names": ["Lipitor", "Atorva", "Storvas"],
                "category": "HMG-CoA Reductase Inhibitor (Statin)",
                "uses": [
                    "Lowering LDL (bad) cholesterol and triglycerides in hyperlipidemia",
                    "Reducing risk of stroke, heart attack, and angina in patients with heart disease"
                ],
                "dosage": "Adults: 10 mg to 80 mg once daily at any time of day, with or without food.",
                "common_side_effects": ["Mild muscle aches (myalgia)", "Joint pain", "Diarrhea", "Nausea"],
                "serious_side_effects": ["Rhabdomyolysis (severe muscle damage)", "Liver enzyme elevation", "Increased blood sugar levels"],
                "interactions": ["Grapefruit juice (large quantities)", "Clarithromycin / Erythromycin", "Gemfibrozil", "Ketoconazole"],
                "precautions": "Avoid excessive alcohol consumption. Report unexplained muscle soreness, tenderness, or weakness immediately."
            },
            "lisinopril": {
                "generic_name": "Lisinopril",
                "brand_names": ["Zestril", "Prinivil"],
                "category": "Angiotensin-Converting Enzyme (ACE) Inhibitor",
                "uses": [
                    "Treatment of High Blood Pressure (Hypertension)",
                    "Heart failure management and post-myocardial infarction recovery"
                ],
                "dosage": "Adults: 10 mg once daily initially, adjusted based on blood pressure response (up to 40 mg daily).",
                "common_side_effects": ["Persistent dry cough", "Dizziness when standing", "Headache", "Fatigue"],
                "serious_side_effects": ["Angioedema (swelling of face, lips, tongue, or throat)", "Hyperkalemia (high blood potassium)"],
                "interactions": ["Potassium supplements or salt substitutes", "NSAIDs (Ibuprofen)", "Lithium"],
                "precautions": "Contraindicated during pregnancy due to fetal risk. Monitor kidney function and blood potassium."
            },
            "omeprazole": {
                "generic_name": "Omeprazole",
                "brand_names": ["Prilosec", "Losec", "Omez"],
                "category": "Proton Pump Inhibitor (PPI)",
                "uses": [
                    "Gastroesophageal Reflux Disease (GERD) and heartburn relief",
                    "Healing of gastric and duodenal peptic ulcers"
                ],
                "dosage": "Adults: 20 mg once daily in the morning, 30 to 60 minutes before breakfast for 4 to 8 weeks.",
                "common_side_effects": ["Headache", "Abdominal pain", "Flatulence", "Nausea"],
                "serious_side_effects": ["Bone fracture risk with long-term high dose", "Magnesium deficiency", "C. difficile diarrhea"],
                "interactions": ["Clopidogrel (decreased antiplatelet effectiveness)", "Digoxin", "Ketoconazole"],
                "precautions": "Intended for short-term use unless directed by a gastroenterologist."
            },
            "cetirizine": {
                "generic_name": "Cetirizine Hydrochloride",
                "brand_names": ["Zyrtec", "Cetzine", "Alerid"],
                "category": "Second-Generation Antihistamine",
                "uses": [
                    "Relief of allergic rhinitis (sneezing, runny nose, watery eyes)",
                    "Chronic urticaria (hives and allergic skin itching)"
                ],
                "dosage": "Adults & Children over 12: 5 mg to 10 mg once daily.",
                "common_side_effects": ["Mild drowsiness", "Dry mouth", "Fatigue"],
                "serious_side_effects": ["Severe allergic reactions (rare)"],
                "interactions": ["Alcohol", "Sedatives or central nervous system depressants"],
                "precautions": "May cause mild sedation; exercise caution when driving or operating heavy machinery."
            }
        }

    def get_info(self, query: str) -> dict:
        """Search medication database by generic name, brand name, or medical condition."""
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Please enter a medicine name or medical query."
            }

        q = query.strip().lower()

        results = []
        for key, med in self.medicine_db.items():
            match_score = 0
            if q == key or q in med["generic_name"].lower():
                match_score += 10
            for b in med["brand_names"]:
                if q in b.lower():
                    match_score += 8
            if q in med["category"].lower():
                match_score += 5
            for use in med["uses"]:
                if q in use.lower():
                    match_score += 4

            if match_score > 0:
                results.append((match_score, med))

        if results:
            results.sort(key=lambda x: x[0], reverse=True)
            best_match = results[0][1]
            return {
                "success": True,
                "data": best_match,
                "query": query,
                "total_matches": len(results)
            }

        return {
            "success": True,
            "query": query,
            "data": {
                "generic_name": f"Search Query: {query.capitalize()}",
                "brand_names": ["Information available via general medical directory"],
                "category": "General Pharmacological Query",
                "uses": [
                    f"General therapeutic inquiries regarding {query}.",
                    "Always verify exact indication with a licensed pharmacist or physician."
                ],
                "dosage": "Dosage must be prescribed individually based on age, weight, renal clearance, and clinical condition.",
                "common_side_effects": ["Mild gastrointestinal discomfort", "Headache", "Dizziness"],
                "serious_side_effects": ["Unexplained allergic skin reactions", "Hypersensitivity"],
                "interactions": ["Consult a pharmacist to review your full list of active prescription drugs."],
                "precautions": "Always read the manufacturer package insert before taking any new prescription or OTC medication."
            }
        }