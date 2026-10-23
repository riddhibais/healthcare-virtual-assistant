import os
import json
import re
import difflib
from langchain_core.documents import Document

class MedicineVectorStore:
    def __init__(self, persist_dir=None, dataset_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.persist_dir = persist_dir or os.path.join(base_dir, "data", "chroma_db")
        self.dataset_path = dataset_path or os.path.join(base_dir, "data", "medicines.json")
        
        # Load local knowledge base into memory for instant matching (<1ms)
        self.medicines_raw = []
        if os.path.exists(self.dataset_path):
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                self.medicines_raw = json.load(f)

    def _to_document(self, med: dict) -> Document:
        content = (
            f"Dawa: {med.get('name')}\n"
            f"Generic Name: {med.get('generic_name')}\n"
            f"Category: {med.get('category')}\n"
            f"Kaam: {med.get('primary_uses')}\n"
            f"Kaise Lein: {med.get('dosage_guidance')}\n"
            f"Side Effects: {med.get('common_side_effects')}\n"
            f"Khatre aur Savdhani: {med.get('serious_risks_contraindications')}\n"
            f"Interactions: {med.get('interactions')}"
        )
        return Document(
            page_content=content,
            metadata={
                "name": med.get("name"),
                "generic_name": med.get("generic_name"),
                "category": med.get("category"),
                "raw": med
            }
        )

    def search(self, query: str, k: int = 2):
        """
        High-precision medical search with zero guessing.
        1. Exact or substring match in name, brand, or generic salt.
        2. Fuzzy typo match (e.g. 'paracitamol' -> 'Paracetamol') with strict cutoff.
        3. Medical symptom match (e.g. 'fever', 'bukhar', 'acidity', 'ulti').
        4. If no genuine match exists, returns [] instead of hallucinating random drugs.
        """
        if not query or not query.strip():
            return []

        clean_query = query.strip().lower()
        # Words in user query
        words = [w for w in re.findall(r'\b\w+\b', clean_query) if len(w) >= 3 and w not in {"what", "the", "and", "can", "take", "with", "used", "about", "give", "tell", "side", "effects", "medicine", "tablet", "kya", "hai", "yeh", "dawa"}]

        scored_matches = []

        for med in self.medicines_raw:
            score = 0
            name_lower = med.get("name", "").lower()
            generic_lower = med.get("generic_name", "").lower()
            category_lower = med.get("category", "").lower()
            uses_lower = med.get("primary_uses", "").lower()

            # 1. Exact or substring match on full brand name or generic salt
            if clean_query in name_lower:
                score += 50
            if clean_query in generic_lower:
                score += 45

            # 2. Token / word level matching
            name_tokens = re.findall(r'\b\w+\b', name_lower + " " + generic_lower)
            for word in words:
                if word in name_tokens:
                    score += 30
                elif word in category_lower:
                    score += 15
                elif word in uses_lower:
                    score += 10
                else:
                    # 3. Fuzzy typo check on medicine names (e.g., paracitamol -> paracetamol)
                    for token in name_tokens:
                        if len(token) >= 4 and len(word) >= 4:
                            ratio = difflib.SequenceMatcher(None, word, token).ratio()
                            if ratio >= 0.72:
                                score += int(ratio * 25)
                                break

            # Only consider genuine, high-confidence matches (score threshold >= 15)
            if score >= 15:
                scored_matches.append((score, med))

        if scored_matches:
            scored_matches.sort(key=lambda x: x[0], reverse=True)
            return [self._to_document(item[1]) for item in scored_matches[:k]]

        # Zero guessing: if no high-confidence match, return empty
        return []
