
import os
from importlib import import_module

from dotenv import load_dotenv
try:
    ChatGoogleGenerativeAI = import_module(
        "langchain_google_genai"
    ).ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None
from langchain_core.prompts import ChatPromptTemplate

from backend.medical_rag.retriever import search_knowledge

load_dotenv()


class MedicineInfo:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        self.llm = None
        if api_key and ChatGoogleGenerativeAI is not None:
            self.llm = ChatGoogleGenerativeAI(
                temperature=0,
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                google_api_key=api_key,
            )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You provide cautious, evidence-grounded medicine information.

Use only the supplied approved reference excerpts to support medical claims.
Do not invent facts, indications, side effects, dosages, contraindications,
or drug interactions. Do not diagnose or prescribe.

If the supplied evidence does not answer the question, say that the
available references are insufficient. Never claim that a medicine is
safe for a particular person based only on these excerpts.

Keep the answer concise and understandable. Do not provide personalized
dosing instructions. Encourage the user to consult a doctor or pharmacist
before starting, stopping, or changing a medicine.

The application will append source references separately. Do not invent
citations or URLs.
                """.strip(),
            ),
            (
                "human",
                "Medicine question:\n{medicine_query}\n\n"
                "Approved reference excerpts:\n{medical_context}",
            ),
        ])

    def get_info(self, medicine_query: str) -> str:
        if not isinstance(medicine_query, str) or not medicine_query.strip():
            return "Please enter a medicine name or a specific medicine question."

        query = medicine_query.strip()

        try:
            results = search_knowledge(query, k=4)
        except Exception:
            return (
                "I couldn't access the approved medical references right now. "
                "Please try again later or ask a pharmacist or doctor for "
                "reliable information. Do not change medication based on "
                "an unverified answer."
            )

        # Fail safely if there is no relevant approved evidence.
        approved_results = [
            item for item in results
            if item.get("review_status") == "approved"
            and item.get("content", "").strip()
        ]

        if not approved_results:
            return (
                "I couldn't find relevant information in the approved "
                "medical references. I can't provide a reliable "
                "evidence-based answer right now. Please consult a doctor "
                "or pharmacist.\n\n"
                "Disclaimer: Do not start, stop, or change a medication "
                "without advice from a qualified healthcare professional."
            )

        references = []
        context_parts = []

        for index, item in enumerate(approved_results, start=1):
            title = item.get("title") or item.get("source") or "Medical reference"
            publisher = item.get("publisher") or "Publisher not specified"
            source_url = item.get("source_url", "")
            reviewed = item.get("last_reviewed", "")

            context_parts.append(
                f"[{index}] Title: {title}\n"
                f"Publisher: {publisher}\n"
                f"Reviewed: {reviewed}\n"
                f"Excerpt:\n{item['content']}"
            )

            if source_url.startswith("https://"):
                references.append(
                    f"[{index}] {title} — {publisher}\n{source_url}"
                    + (f"\nLast reviewed: {reviewed}" if reviewed else "")
                )

        # Do not call the language model without an API key.
        if self.llm is None:
            return (
                "The approved medical references were found, but the AI "
                "answering service is not configured. Please check "
                "GOOGLE_API_KEY in your environment settings."
            )

        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "medicine_query": query,
                "medical_context": "\n\n".join(context_parts),
            })

            answer = response.content
            if not isinstance(answer, str):
                answer = str(answer)

            answer = answer.strip()

            if not answer:
                return (
                    "The AI service returned no answer. Please try again "
                    "later or consult a pharmacist."
                )

            # Remove any unexpected reasoning tags.
            import re
            answer = re.sub(
                r"<think>.*?</think>",
                "",
                answer,
                flags=re.DOTALL | re.IGNORECASE,
            ).strip()

            if not answer or "<think>" in answer.lower():
                return (
                    "I couldn't produce a suitable answer from the "
                    "approved references. Please consult a pharmacist "
                    "or doctor."
                )

            answer += (
                "\n\nDisclaimer: This information is educational, not "
                "personalized medical advice. Consult a qualified "
                "healthcare professional before changing medication."
            )

            if references:
                answer += "\n\nReferences:\n" + "\n\n".join(references)

            return answer

        except Exception:
            return (
                "I couldn't generate medicine information at this time. "
                "Please try again later or consult a pharmacist or doctor."
            )
