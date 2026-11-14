import os
import re
import io
import json
import base64
import urllib.request
from dotenv import load_dotenv
from PIL import Image, ImageOps

load_dotenv()

def get_secret(key_name: str) -> str:
    """
    Robustly retrieve secret from environment (.env) or Streamlit Cloud Secrets (st.secrets).
    Handles uppercase, lowercase, and nested section configurations.
    """
    # 1. Check os.environ
    for k in (key_name, key_name.lower(), key_name.upper()):
        val = os.getenv(k, "").strip()
        if val:
            return val

    # 2. Check Streamlit Cloud st.secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in (key_name, key_name.lower(), key_name.upper()):
                if k in st.secrets:
                    val = str(st.secrets[k]).strip()
                    if val:
                        return val
            for sec_key, sec_val in st.secrets.items():
                if sec_key.lower() == key_name.lower() and isinstance(sec_val, str):
                    return sec_val.strip()
                if isinstance(sec_val, dict):
                    for sub_k, sub_v in sec_val.items():
                        if sub_k.lower() == key_name.lower() and isinstance(sub_v, str):
                            return sub_v.strip()
    except Exception as e:
        print(f"Error accessing st.secrets for {key_name}: {e}")

    return ""

class ReportExplainer:
    def __init__(self):
        self.groq_api_key = get_secret("GROQ_API_KEY")
        self.google_api_key = get_secret("GOOGLE_API_KEY")

        # Strict prompt without hallucinations or long essays
        self.system_prompt = (
            "You are a helpful, friendly, and medically accurate virtual assistant. "
            "A patient has provided their medical laboratory test report (as text or image). "
            "CRITICAL INSTRUCTIONS:\n"
            "1. Read and explain ONLY the EXACT medical parameters, values, and reference ranges that are visibly printed in their document.\n"
            "2. DO NOT hallucinate, assume, invent, or simulate any test names, numbers, or results. If a test is not in the document, do NOT invent it.\n"
            "3. If the document is blurry, illegible, or does NOT contain laboratory test results, clearly state: "
            "'⚠️ The uploaded document does not appear to contain readable diagnostic lab results. Please upload a clear photo or digital PDF of your laboratory test paper.'\n"
            "4. Explain in 100% SIMPLE, REAL, and CONCISE ENGLISH (NO Hindi, NO complex jargon). Keep it brief, clear, and easy to understand in 15-20 seconds.\n\n"
            "When valid test results are present, format your response strictly using this clean layout:\n\n"
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

    def _optimize_and_encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Preprocesses image: fixes EXIF orientation from phone cameras,
        resizes if too large while maintaining high sharpness, and encodes to base64.
        """
        with Image.open(image_path) as img:
            # Auto-orient smartphone photos based on EXIF
            img = ImageOps.exif_transpose(img)

            # Convert RGBA/P to standard RGB
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Resize if dimensions exceed 1800px to ensure fast transmission and fit API limits
            max_dim = 1800
            if max(img.width, img.height) > max_dim:
                scale = max_dim / max(img.width, img.height)
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=92, optimize=True)
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return encoded, "image/jpeg"

    def explain_text(self, report_text: str) -> str:
        """Explains text-extracted lab report using Groq multi-model failover with Gemini fallback."""
        if not report_text or not report_text.strip():
            return "⚠️ No readable text found in the report. Please ensure the document is clear."

        # Verify that the text contains at least some diagnostic numbers or keywords
        has_digits = bool(re.search(r'\d+', report_text))
        if not has_digits and len(report_text.strip()) < 30:
            return (
                "⚠️ **Insufficient Report Details**: The extracted text does not contain readable test numbers or values. "
                "Please upload a clearer document or type your test parameters and numbers into the box below."
            )

        groq_key = self.groq_api_key or get_secret("GROQ_API_KEY")
        google_key = self.google_api_key or get_secret("GOOGLE_API_KEY")

        if not groq_key and not google_key:
            return (
                "⚠️ **API Key Missing**: No GROQ_API_KEY or GOOGLE_API_KEY was found. "
                "If running on Streamlit Cloud, please add GROQ_API_KEY in App Settings ➡️ Secrets."
            )

        # 1. Try Groq (ultra-fast, quota-free, 0.8s response)
        if groq_key:
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
                        "max_tokens": 900
                    }
                    req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/chat/completions",
                        data=json.dumps(payload).encode("utf-8"),
                        headers={
                            "Authorization": f"Bearer {groq_key}",
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

        # 2. Try Gemini REST fallback
        if google_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={google_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"{self.system_prompt}\n\nMedical Report Text:\n{report_text}"}
                        ]
                    }]
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=12) as response:
                    res = json.loads(response.read().decode("utf-8"))
                    text = res["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                    if cleaned:
                        return cleaned
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    return (
                        "⚠️ **Server Busy (Rate Limit Reached)**: The free-tier request quota is temporarily full. "
                        "Please wait a few moments and try again."
                    )
                print(f"Gemini text fallback error: {e}")

        return "⚠️ Unable to analyze report text at this time. Please check your internet connection or API settings."

    def explain_image(self, image_path: str) -> str:
        """
        Directly reads and explains medical report images (JPG/PNG/JPEG) using Multimodal Vision.
        Reads actual parameters from the image without hallucinating.
        """
        if not os.path.exists(image_path):
            return "⚠️ Error: The specified image file could not be found."

        try:
            b64_data, mime_type = self._optimize_and_encode_image(image_path)
        except Exception as img_err:
            return f"⚠️ Error processing image file: {str(img_err)}"

        groq_key = self.groq_api_key or get_secret("GROQ_API_KEY")
        google_key = self.google_api_key or get_secret("GOOGLE_API_KEY")

        if not groq_key and not google_key:
            return (
                "⚠️ **API Key Missing on Streamlit Cloud**:\n\n"
                "Neither `GROQ_API_KEY` nor `GOOGLE_API_KEY` was found in Secrets or environment.\n\n"
                "**How to fix**:\n"
                "1. Go to your Streamlit Cloud app dashboard.\n"
                "2. Click **Settings** ➡️ **Secrets**.\n"
                "3. Add: `GROQ_API_KEY = \"gsk_...\"` and click **Save**.\n"
                "4. Re-upload or re-analyze your report."
            )

        groq_err_msg = ""
        # 1. Primary: Groq Multimodal Vision (Qwen 3.8 27B Vision - fast, high accuracy on tables)
        if groq_key:
            try:
                payload = {
                    "model": "qwen/qwen3.8-27b",
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Please inspect this uploaded medical lab report image carefully. "
                                        "Read the EXACT test parameters, patient observed values, and normal reference ranges printed on it. "
                                        "Provide a clear, structured explanation based strictly on what is visibly printed. "
                                        "Do not fabricate any values."
                                    )
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{b64_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=22) as response:
                    res = json.loads(response.read().decode("utf-8"))
                    text = res["choices"][0]["message"]["content"]
                    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                    if cleaned:
                        return cleaned
            except Exception as groq_err:
                groq_err_msg = str(groq_err)
                print(f"Groq Vision error: {groq_err}")

        # 2. Fallback: Google Gemini Multimodal Vision REST
        gemini_err_msg = ""
        if google_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={google_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {
                                "text": (
                                    f"{self.system_prompt}\n\n"
                                    "Please read and explain this medical lab report image carefully. "
                                    "Extract only the real test results visibly printed in the image."
                                )
                            },
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": b64_data
                                }
                            }
                        ]
                    }]
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=18) as response:
                    res = json.loads(response.read().decode("utf-8"))
                    text = res["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                    if cleaned:
                        return cleaned
            except Exception as gemini_err:
                gemini_err_msg = str(gemini_err)
                print(f"Gemini Vision fallback error: {gemini_err}")

        # 3. Offline / Local Fallback: RapidOCR
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr_engine = RapidOCR()
            ocr_res, _ = ocr_engine(image_path)
            if ocr_res:
                extracted_lines = [line[1] for line in ocr_res if line and len(line) > 1 and line[1].strip()]
                extracted_text = "\n".join(extracted_lines)
                if extracted_text and len(extracted_text.strip()) > 30 and re.search(r'\d+', extracted_text):
                    return self.explain_text(extracted_text)
        except Exception as ocr_err:
            print(f"RapidOCR extraction notice: {ocr_err}")

        err_hint = ""
        if groq_err_msg or gemini_err_msg:
            err_hint = f"\n\n*(Diagnostics: {groq_err_msg or gemini_err_msg})*"

        return (
            "⚠️ **Could not read test numbers clearly from the photo**:\n\n"
            "- Please ensure the photo is well-lit, sharp, and focused on the test names and numbers.\n"
            "- If your report is on multiple pages, upload page-by-page or use a digital PDF.\n"
            "- Alternatively, you can copy/type your test numbers into the text box below!"
            f"{err_hint}"
        )

    def explain_pdf(self, pdf_path: str) -> str:
        """Extracts text from PDF or renders pages to vision for scanned PDFs."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            extracted_text = ""
            for page in doc:
                extracted_text += page.get_text() + "\n"
            doc.close()

            # If digital text exists and contains numbers
            if extracted_text and len(extracted_text.strip()) > 30 and re.search(r'\d+', extracted_text):
                return self.explain_text(extracted_text)

            # If scanned PDF (no embedded text), render first page to high-res image and use Vision
            doc = fitz.open(pdf_path)
            if len(doc) > 0:
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                temp_img_path = pdf_path.replace(".pdf", "_page1.png")
                pix.save(temp_img_path)
                doc.close()

                result = self.explain_image(temp_img_path)
                if os.path.exists(temp_img_path):
                    try:
                        os.remove(temp_img_path)
                    except Exception:
                        pass
                return result

            doc.close()
            return "⚠️ The uploaded PDF appears to be empty or unreadable."
        except Exception as e:
            return f"⚠️ Error processing PDF: {str(e)}"
