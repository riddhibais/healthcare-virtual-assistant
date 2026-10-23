
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
