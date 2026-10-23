import re

class SymptomChecker:
    def __init__(self):
        # Emergency triggers requiring immediate medical care
        self.emergency_keywords = [
            "chest pain", "shortness of breath", "difficulty breathing", "severe chest pressure",
            "stroke", "slurred speech", "facial drooping", "sudden weakness", "sudden numbness",
            "loss of consciousness", "fainted", "unresponsive", "severe head injury",
            "anaphylaxis", "swelling of lip", "throat closing", "coughing blood"
        ]

        self.urgent_keywords = [
            "high fever", "severe pain", "persistent vomiting", "blood in stool",
            "stiff neck", "deep cut", "inability to keep fluids down", "migraine with aura"
        ]

        self.symptom_clusters = {
            "respiratory": {
                "keywords": ["cough", "fever", "sore throat", "runny nose", "congestion", "sneezing", "wheezing"],
                "specialist": "General Practitioner / Pulmonologist",
                "conditions": ["Common Cold / Upper Respiratory Infection", "Influenza (Flu)", "Acute Bronchitis", "Allergic Rhinitis"],
                "questions": [
                    "How long have these cough or respiratory symptoms lasted?",
                    "Are you experiencing any shortness of breath or pain when inhaling?",
                    "Should I test for viral infections like Flu or COVID-19?"
                ]
            },
            "gastrointestinal": {
                "keywords": ["nausea", "vomiting", "diarrhea", "stomach pain", "abdominal cramp", "acid reflux", "bloating", "indigestion"],
                "specialist": "Gastroenterologist / General Physician",
                "conditions": ["Gastroenteritis (Stomach Bug)", "Acid Reflux / GERD", "Dietary Indigestion / Food Intolerance", "Irritable Bowel Symptoms"],
                "questions": [
                    "Could my digestive symptoms be related to food sensitivity or infection?",
                    "What electrolyte or dietary adjustments do you recommend?",
                    "At what point would additional imaging or stool tests be needed?"
                ]
            },
            "neurological": {
                "keywords": ["headache", "dizziness", "migraine", "lightheaded", "tingling", "fatigue", "brain fog"],
                "specialist": "Neurologist / Primary Care Physician",
                "conditions": ["Tension Headache", "Migraine", "Stress / Lack of Sleep", "Dehydration or Low Blood Sugar"],
                "questions": [
                    "Are my headaches characteristic of tension or migraine headaches?",
                    "Could environmental triggers or stress be contributing?",
                    "Which preventative measures or medication would be safe for me?"
                ]
            },
            "musculoskeletal": {
                "keywords": ["back pain", "joint pain", "muscle soreness", "stiff joint", "knee pain", "swollen ankle", "cramp"],
                "specialist": "Orthopedist / Rheumatologist / Physical Therapist",
                "conditions": ["Muscle Strain / Sprain", "Joint Inflammation / Arthritis", "Postural Fatigue", "Overexertion"],
                "questions": [
                    "Is physical therapy or gentle stretching recommended for this strain?",
                    "Should I apply ice or heat treatment?",
                    "Would an X-ray or MRI be beneficial if symptoms persist?"
                ]
            },
            "dermatological": {
                "keywords": ["rash", "itching", "red skin", "hives", "skin lesion", "dry skin", "blister"],
                "specialist": "Dermatologist / Allergist",
                "conditions": ["Contact Dermatitis", "Allergic Hives", "Eczema / Dry Skin Reaction", "Mild Skin Infection"],
                "questions": [
                    "Is this rash likely an allergic reaction or an infection?",
                    "Which topical cream or antihistamine is safest to soothe this?",
                    "Are there specific irritants or soaps I should avoid?"
                ]
            }
        }

    def check_symptoms(self, symptoms_text: str) -> dict:
        """Analyze symptom text and return clinical urgency, conditions, and recommendations."""
        if not symptoms_text or not symptoms_text.strip():
            return {
                "success": False,
                "error": "Please enter your symptoms before submitting."
            }

        text_lower = symptoms_text.lower()

        # Check for Emergency Red Flags
        for kw in self.emergency_keywords:
            if kw in text_lower:
                return {
                    "success": True,
                    "urgency_level": "EMERGENCY 🚨",
                    "urgency_color": "#FF4D4D",
                    "badge_bg": "#FFE6E6",
                    "summary": f"CRITICAL NOTICE: Symptoms include red-flag warning indicators ({kw}). Immediate medical attention required.",
                    "action_required": "Call emergency medical services (911 / Local Emergency Number) or go to the nearest Emergency Room immediately.",
                    "potential_conditions": ["Critical Emergency Condition requiring urgent triage"],
                    "specialist": "Emergency Medicine Physician",
                    "questions_for_doctor": ["What is the immediate emergency stabilization plan?"],
                    "warning_signs": ["Do not drive yourself if experiencing severe pain, fainting, or chest discomfort."]
                }

        # Check for Urgent Care Flags
        is_urgent = any(kw in text_lower for kw in self.urgent_keywords)

        # Match symptom categories
        matched_categories = []
        matched_conditions = []
        matched_questions = []
        suggested_specialists = []

        for category_name, data in self.symptom_clusters.items():
            if any(kw in text_lower for kw in data["keywords"]):
                matched_categories.append(category_name.capitalize())
                matched_conditions.extend(data["conditions"])
                matched_questions.extend(data["questions"])
                suggested_specialists.append(data["specialist"])

        # Determine Triage Level
        if is_urgent:
            urgency_level = "URGENT CARE ⚠️"
            urgency_color = "#FF9900"
            badge_bg = "#FFF0D6"
            action_required = "Seek medical evaluation at an Urgent Care clinic within 12 to 24 hours."
        elif matched_categories:
            urgency_level = "PRIMARY CARE CONSULTATION 🩺"
            urgency_color = "#1E88E5"
            badge_bg = "#E3F2FD"
            action_required = "Schedule a routine consultation with your primary care provider."
        else:
            urgency_level = "SELF-CARE & MONITORING 🌿"
            urgency_color = "#2E7D32"
            badge_bg = "#E8F5E9"
            action_required = "Rest, maintain adequate hydration, and monitor your symptoms over the next 24-48 hours."
            matched_conditions = ["Mild transient discomfort", "General physical fatigue or minor strain"]
            matched_questions = [
                "What rest or hydration regimen is best suited for me?",
                "What specific changes in my symptoms should prompt a clinic visit?"
            ]
            suggested_specialists = ["Primary Care Physician / Family Practitioner"]

        return {
            "success": True,
            "urgency_level": urgency_level,
            "urgency_color": urgency_color,
            "badge_bg": badge_bg,
            "summary": f"Assessment for provided symptoms ({', '.join(matched_categories) if matched_categories else 'General'}).",
            "action_required": action_required,
            "categories": matched_categories,
            "potential_conditions": list(set(matched_conditions))[:4],
            "specialist": suggested_specialists[0] if suggested_specialists else "Primary Care Physician",
            "questions_for_doctor": matched_questions[:3],
            "warning_signs": [
                "Seek immediate care if you develop sudden severe chest pain, shortness of breath, high fever, or loss of consciousness."
            ]
        }

import os
import re

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    ChatGoogleGenerativeAI = None  # type: ignore[assignment]

from backend.medical_rag.retriever import search_knowledge

load_dotenv()

DISCLAIMER = (
    "\n\nDisclaimer: This information is for general informational "
    "purposes only and does not constitute medical advice. "
    "Consult a qualified healthcare professional for diagnosis "
    "and treatment."
)

NO_APPROVED_INFO = (
    "I couldn't find relevant information in the approved medical "
    "references. I can't provide a reliable evidence-based assessment "
    "right now. Please consult a qualified healthcare professional."
    + DISCLAIMER
)


class SymptomChecker:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        self.llm = None

        if api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import-not-found]

                self.llm = ChatGoogleGenerativeAI(
                    temperature=0.0,
                    model=model_name,
                    google_api_key=api_key,
                )
            except ImportError:
                # Keep the module usable even when the optional Gemini
                # integration is not installed.
                self.llm = None

        system_prompt = """
You are a cautious AI health information assistant.

Rules:
1. Do not diagnose the user or claim certainty about a condition.
2. Base medical information on the supplied approved reference excerpts.
3. Do not invent medical facts, treatments, medication doses, or citations.
4. If the excerpts do not support an answer, clearly say so.
5. Give concise, understandable general information.
6. Suggest consulting a qualified healthcare professional when appropriate.
7. Do not recommend starting, stopping, or changing medication.
8. Do not treat the supplied excerpts as a substitute for professional care.
9. If symptoms described suggest a possible emergency, advise seeking
   emergency medical care promptly.
10. Do not reveal internal reasoning or use <think> tags.

Answer the user's symptom-related question using the reference excerpts.
Distinguish information supported by the excerpts from uncertainty.
"""

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "User's symptoms:\n{symptoms}\n\n"
                    "Approved medical reference excerpts:\n{context}\n\n"
                    "Provide a concise, cautious response.",
                ),
            ]
        )

        self.chain = (
            self.prompt | self.llm
            if self.llm is not None
            else None
        )

    def check_symptoms(self, symptoms: str) -> str:
        if not isinstance(symptoms, str) or not symptoms.strip():
            return "Please describe the symptoms you want information about."

        try:
            results = search_knowledge(symptoms.strip(), k=4)

            # Never use documents that are not explicitly approved.
            approved_results = [
                item
                for item in results
                if item.get("review_status") == "approved"
                and item.get("content", "").strip()
            ]

            if not approved_results:
                return NO_APPROVED_INFO

            if self.chain is None:
                return (
                    "Approved medical references were found, but the AI "
                    "service is not configured. Check your GOOGLE_API_KEY "
                    "environment variable."
                    + DISCLAIMER
                )

            context_parts = []

            for item in approved_results:
                title = item.get("title") or item.get("source", "Unknown")
                publisher = item.get("publisher", "Unknown publisher")

                context_parts.append(
                    f"Reference: {title}\n"
                    f"Publisher: {publisher}\n"
                    f"Content: {item['content']}"
                )

            context = "\n\n---\n\n".join(context_parts)

            response = self.chain.invoke(
                {
                    "symptoms": symptoms.strip(),
                    "context": context,
                }
            )

            clean_text = response.content

            if not isinstance(clean_text, str):
                clean_text = str(clean_text)

            clean_text = re.sub(
                r"<think>.*?</think>",
                "",
                clean_text,
                flags=re.DOTALL,
            ).strip()

            if not clean_text:
                return (
                    "The AI service did not return a usable response. "
                    "Please consult a healthcare professional."
                    + DISCLAIMER
                )

            # Attach traceable references used for this answer.
            source_lines = []
            seen_sources = set()

            for item in approved_results:
                source = item.get("title") or item.get("source", "Unknown")
                source_url = item.get("source_url", "")
                source_key = (source, source_url)

                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    line = f"- {source}"
                    if source_url:
                        line += f" ({source_url})"
                    source_lines.append(line)

            clean_text = clean_text.replace(DISCLAIMER, "").strip()

            if source_lines:
                clean_text += (
                    "\n\nApproved references used:\n"
                    + "\n".join(source_lines)
                )

            return clean_text + DISCLAIMER

        except Exception:
            # Avoid exposing API keys, internal paths, or stack traces.
            return (
                "I couldn't access the approved medical references or "
                "complete the symptom assessment. Please try again later "
                "or consult a qualified healthcare professional."
                + DISCLAIMER
            )
