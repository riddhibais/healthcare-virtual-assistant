
import os
import re
import importlib
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from backend.medical_rag.retriever import search_knowledge

load_dotenv()

DISCLAIMER = (
    "\n\nDisclaimer: I am an AI, not a doctor. This explanation is "
    "for informational purposes only. Consult a qualified healthcare "
    "professional before making medical decisions."
)


class ReportExplainer:
    def __init__(self):
        self.chain = None

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return

        try:
            genai_module = importlib.import_module("langchain_google_genai")
            ChatGoogleGenerativeAI = genai_module.ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                temperature=0.0,
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                google_api_key=api_key,
                max_tokens=4096,
            )

            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """
You explain medical reports in simple language.

Use these headings:
### 📝 Simple Summary & Risks
### ⚠️ Abnormal Findings

Rules:
- Do not diagnose the patient.
- Do not invent causes, abnormal values, or reference ranges.
- Explain only what the report and supplied approved references support.
- State clearly when evidence is insufficient.
- Do not recommend starting, stopping, or changing medication.
- Recommend professional assessment when appropriate.
- Do not reveal internal reasoning.
""",
                ),
                (
                    "human",
                    "Report text:\n{report_text}\n\n"
                    "Approved medical references:\n{context}",
                ),
            ])

            self.chain = prompt | llm

        except ImportError:
            self.chain = None

    def _extract_report_text(self, pdf_path: str) -> str:
        """Extract text from a PDF using pypdf."""
        from pypdf import PdfReader

        path = Path(pdf_path)

        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found: {path}")

        reader = PdfReader(str(path))

        if not reader.pages:
            raise ValueError("The PDF contains no pages.")

        pages = []

        for number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            if text:
                pages.append(f"Page {number}:\n{text}")

        report_text = "\n\n".join(pages).strip()

        if not report_text:
            raise ValueError(
                "No readable text was extracted. This may be a scanned PDF "
                "that requires OCR."
            )

        return report_text[:20000]

    def explain_pdf(self, pdf_path: str) -> str:
        try:
            report_text = self._extract_report_text(pdf_path)

            results = search_knowledge(report_text[:1500], k=4)

            approved = [
                item for item in results
                if item.get("review_status") == "approved"
                and item.get("content", "").strip()
            ]

            if not approved:
                return (
                    "I could read the report, but no relevant approved "
                    "medical references were found. I cannot provide a "
                    "reliable evidence-based interpretation yet. Please "
                    "consult a qualified healthcare professional."
                    + DISCLAIMER
                )

            if self.chain is None:
                return (
                    "The report was read, but the AI service is unavailable. "
                    "Check GOOGLE_API_KEY and the "
                    "langchain-google-genai installation."
                    + DISCLAIMER
                )

            context = "\n\n---\n\n".join(
                f"Title: {item.get('title', item.get('source', 'Unknown'))}\n"
                f"Publisher: {item.get('publisher', 'Unknown')}\n"
                f"Content: {item['content']}"
                for item in approved
            )

            response = self.chain.invoke({
                "report_text": report_text,
                "context": context,
            })

            answer = response.content
            if not isinstance(answer, str):
                answer = str(answer)

            answer = re.sub(
                r"<think>.*?</think>",
                "",
                answer,
                flags=re.DOTALL,
            ).strip()

            if not answer:
                return "No usable explanation was generated." + DISCLAIMER

            sources = []
            seen = set()

            for item in approved:
                title = item.get("title") or item.get("source", "Unknown")
                url = item.get("source_url", "")
                key = (title, url)

                if key not in seen:
                    seen.add(key)
                    sources.append(f"- {title}" + (f" ({url})" if url else ""))

            answer += "\n\n### Approved References Used\n" + "\n".join(sources)
            return answer + DISCLAIMER

        except FileNotFoundError:
            return "Error: The specified PDF file could not be found."
        except ImportError as exc:
            return (
                f"Missing dependency: {exc}. Install pypdf using "
                "`python -m pip install pypdf`."
            )
        except ValueError as exc:
            return f"Unable to read the report: {exc}"
        except Exception:
            return (
                "An error occurred while processing the report. "
                "Check the PDF, dependencies, and application logs."
                + DISCLAIMER
            )
