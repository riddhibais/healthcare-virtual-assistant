import os
import re
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

class ReportExplainer:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()

        # Simple, real, concise prompt without long essays
        self.system_prompt = (
            "You are a helpful, friendly medical virtual assistant. "
            "A patient has provided their real medical laboratory report. "
            "Explain ONLY what is actually written in their report in 100% SIMPLE, REAL, and CONCISE ENGLISH (NO Hindi, NO complex textbook jargon). "
            "Do NOT write long essays or overly descriptive paragraphs. Keep it brief, clear, and easy to understand in 15-20 seconds.\n\n"
            "Format your response strictly using this clean layout:\n\n"
            "📋 **Report Summary**\n"
            "- [1-2 short sentences: what test this is and what the overall result shows in plain English]\n\n"
            "⚠️ **Key & Abnormal Findings**\n"
            "| Parameter | Your Result | Normal Range | Status | Simple Meaning |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "(List the key markers with status: 🔺 High, 🔻 Low, or 🟢 Normal and 1-line simple meaning)\n\n"
            "🩺 **What This Means for You**\n"
            "- [2 short sentences explaining what these results mean for their daily health without scary medical jargon]\n\n"
            "🥗 **Simple Home & Diet Tips**\n"
            "- [2-3 short practical food and lifestyle steps based on these exact numbers]\n\n"
            "👨‍⚕️ **Next Steps**\n"
            "- Which doctor to see (e.g. General Physician) and 1-2 simple questions to ask.\n\n"
            "---\n"
            "*⚠️ Disclaimer: Educational guidance only. Consult your doctor for formal diagnosis and treatment.*"
        )

    def explain_text(self, report_text: str) -> str:
        """Explains text-extracted lab report using Groq multi-model failover."""
        if not report_text or not report_text.strip():
            return "⚠️ No readable text found in the report. Please ensure the document is clear."

        # 1. Try Groq (ultra-fast, quota-free, 0.8s response)
        if self.groq_api_key:
            models_to_try = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
            for model_name in models_to_try:
                try:
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": f"Please explain ONLY this medical lab report concisely:\n\n{report_text}"}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 800
                    }
                    req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/chat/completions",
                        data=json.dumps(payload).encode("utf-8"),
                        headers={
                            "Authorization": f"Bearer {self.groq_api_key}",
                            "Content-Type": "application/json",
                            "User-Agent": "Mozilla/5.0"
                        }
                    )
                    with urllib.request.urlopen(req, timeout=14) as response:
                        res = json.loads(response.read().decode("utf-8"))
                        text = res["choices"][0]["message"]["content"]
                        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                        if cleaned:
                            return cleaned
                except Exception as e:
                    print(f"Groq report explanation error on {model_name}: {e}")
                    continue

        # 2. Try Gemini fallback
        if self.google_api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.google_api_key)
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=f"{self.system_prompt}\n\nMedical Report Text:\n{report_text}"
                )
                clean_text = re.sub(r'<think>.*?</think>', '', response.text, flags=re.DOTALL).strip()
                return clean_text
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    return (
                        "⚠️ **Server Busy (Rate Limit Reached)**: The free-tier request quota is temporarily full. "
                        "Please wait a few moments and try again."
                    )
                return f"⚠️ Error analyzing report: {err_str}"

        return "⚠️ No valid API key configured in `.env`."

    def explain_pdf(self, pdf_path: str) -> str:
        """Extracts text from PDF and generates structured explanation."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            extracted_text = ""
            for page in doc:
                extracted_text += page.get_text() + "\n"
            doc.close()

            if extracted_text and len(extracted_text.strip()) > 15:
                return self.explain_text(extracted_text)

            # If no embedded text (scanned PDF), use RapidOCR on the first page
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                temp_img_path = pdf_path.replace(".pdf", "_page1.png")
                pix.save(temp_img_path)
                doc.close()
                result = self.explain_image(temp_img_path)
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
                return result
            doc.close()
            return "⚠️ The uploaded PDF appears to be empty or unreadable."
        except Exception as e:
            return f"⚠️ Error processing PDF: {str(e)}"

    def explain_image(self, image_path: str) -> str:
        """Extracts text from medical report image (JPG/PNG) via local RapidOCR, then analyzes via Groq."""
        # 1. First extract text locally using RapidOCR (100% offline, zero API quota, instant)
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr_engine = RapidOCR()
            ocr_res, _ = ocr_engine(image_path)
            if ocr_res:
                extracted_lines = [line[1] for line in ocr_res if line and len(line) > 1 and line[1].strip()]
                extracted_text = "\n".join(extracted_lines)
                if extracted_text and len(extracted_text.strip()) > 10:
                    return self.explain_text(extracted_text)
        except Exception as ocr_err:
            print(f"RapidOCR extraction notice: {ocr_err}")

        # 2. Fallback to Gemini Vision if available
        if self.google_api_key:
            try:
                from PIL import Image
                from google import genai

                client = genai.Client(api_key=self.google_api_key)
                img = Image.open(image_path)

                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=[img, f"{self.system_prompt}\n\nPlease read and explain this medical lab report image."]
                )
                clean_text = re.sub(r'<think>.*?</think>', '', response.text, flags=re.DOTALL).strip()
                return clean_text
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    return (
                        "⚠️ **Could not read text clearly from the photo**: "
                        "Please ensure the image is bright and sharp, or paste your test names and numbers into the text box below!"
                    )

        return (
            "⚠️ **Could not detect readable text in the image**: "
            "Please upload a clearer, well-lit photo of your report, or type/paste your report numbers into the box below."
        )
