import os
import re
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

class MedicineInfo:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    def _query_groq(self, medicine_query: str) -> str:
        """Ultra-fast (under 1 second) medical reasoning using Groq API with multi-model failover."""
        system_prompt = (
            "You are an expert clinical pharmacist and virtual medical assistant. "
            "A user is asking about a medicine or health product: '{query}'.\n\n"
            "Guidelines:\n"
            "1. Output your answer in 100% SIMPLE, CLEAR ENGLISH (do NOT use Hindi).\n"
            "2. Keep explanations direct, concise, and layman-friendly. Avoid overly dense medical textbook jargon.\n"
            "3. Format your response strictly using this structured 5-step layout:\n\n"
            "### 💊 **[Medicine Name]**\n"
            "- **Active Ingredient / Generic Salt**: [Generic Name]\n"
            "- **Therapeutic Class**: [Drug Category / Class]\n\n"
            "---\n\n"
            "#### 🎯 **1. Primary Uses**\n"
            "[Clear bullet points explaining what symptoms, conditions, or infections this treats]\n\n"
            "#### ⏱️ **2. Dosage & How to Take**\n"
            "[Timing instructions: with/after food, frequency, and safe dosage rules]\n\n"
            "#### ⚠️ **3. Common Side Effects**\n"
            "[Mild and common symptoms to be aware of]\n\n"
            "#### 🚫 **4. Important Warnings & Precautions**\n"
            "[Key safety alerts: alcohol warnings, liver/kidney disease, pregnancy/breastfeeding]\n\n"
            "#### 🔄 **5. Drug & Food Interactions**\n"
            "[Important medicines, drinks, or foods to avoid taking together]\n\n"
            "---\n"
            "*⚠️ Disclaimer: This information is for educational purposes only. Never start, stop, or change medications without consulting a licensed physician or pharmacist.*\n\n"
            "4. If the term '{query}' is a typo, brand variant, or uncommon trade name (e.g., Danzen, Dantrolene, or similar), explain the likely medicine clearly.\n"
            "5. If the term is completely unrecognizable as any medical term or drug, state:\n"
            "'❌ **\"{query}\"** was not recognized as a known medicine, salt, or healthcare product. Please check the spelling or ask your doctor/pharmacist.'"
        )

        prompt_text = system_prompt.replace("{query}", medicine_query)

        # Primary and backup models on Groq
        models_to_try = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        last_error = None

        for model_name in models_to_try:
            try:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": prompt_text}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 750
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

                with urllib.request.urlopen(req, timeout=12) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    content = result["choices"][0]["message"]["content"]
                    # Remove any thinking tags if present
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                    if content:
                        return content
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error
        return ""

    def _query_gemini(self, medicine_query: str) -> str:
        """Fallback to Google Gemini if Groq is unavailable."""
        from google import genai
        client = genai.Client(api_key=self.google_api_key)
        
        system_instruction = (
            "You are an expert clinical pharmacist. "
            "Explain the medicine in 100% SIMPLE, CLEAR ENGLISH with clear headings:\n"
            "### 💊 [Medicine Name]\n"
            "- Active Ingredient / Generic Salt\n"
            "- Therapeutic Class\n"
            "1. Primary Uses\n"
            "2. Dosage & How to Take\n"
            "3. Common Side Effects\n"
            "4. Important Warnings & Precautions\n"
            "5. Drug & Food Interactions\n"
            "End with standard disclaimer."
        )

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=f"{system_instruction}\n\nMedicine Query: {medicine_query}"
        )
        return response.text

    def get_info(self, medicine_query: str) -> str:
        if not medicine_query or not medicine_query.strip():
            return "Please enter a valid medicine name or medication question (e.g., *Allegra, Dolo 650, Combiflam, Danzen, Augmentin*)."

        clean_query = medicine_query.strip()

        # 1. Try Groq first (Ultra-fast, under 1 second response, multiple models)
        if self.groq_api_key:
            try:
                return self._query_groq(clean_query)
            except Exception as e:
                print(f"Groq API error: {e}, attempting Gemini fallback...")

        # 2. Try Gemini fallback
        if self.google_api_key:
            try:
                return self._query_gemini(clean_query)
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    return (
                        "⚠️ **Server Busy (Rate Limit Reached)**: The free-tier request quota is temporarily full. "
                        "Please wait a few seconds and try again. All features will resume momentarily."
                    )
                return f"⚠️ Unable to retrieve medicine details at this moment. Error: {err_str}"

        return "⚠️ No valid API key configured. Please check GROQ_API_KEY or GOOGLE_API_KEY in `.env`."
