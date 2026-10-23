import os
import re
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

class SymptomChecker:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        self.system_prompt = (
            "You are a friendly, knowledgeable medical virtual assistant. "
            "A user is describing their symptoms. Provide a SHORT, CLEAR, and CRISP response in plain, simple English (NO Hindi). "
            "Do NOT write long essays or dense textbook paragraphs. Keep it brief, conversational, and easy to read in 10-15 seconds.\n\n"
            "Format your response strictly using this markdown layout with a separate line for every bullet:\n\n"
            "🩺 **Possible Causes**:\n"
            "- **[Condition 1]**: Brief 1-line reason.\n"
            "- **[Condition 2]**: Brief 1-line reason.\n\n"
            "💡 **Why It's Happening**:\n"
            "- Simple 1-2 sentence explanation of root cause (e.g. viral infection, dehydration, muscle strain, allergy).\n\n"
            "🏠 **Quick Home Relief**:\n"
            "- [Short tip 1: hydration/diet]\n"
            "- [Short tip 2: rest/comfort tip]\n"
            "- [Short tip 3: safe OTC tip]\n\n"
            "🚨 **When to See a Doctor**:\n"
            "- [1-2 red-flag warning signs to watch for]\n"
            "- Recommended Specialist: **[General Physician / ENT / Gastroenterologist / etc.]**\n\n"
            "💬 **Follow-up Question**: [Ask ONE short, helpful question]\n\n"
            "---\n"
            "*⚠️ Disclaimer: For informational guidance only. Always consult a licensed doctor for medical diagnosis.*"
        )

    def check_emergency(self, text: str) -> bool:
        """Detects critical red-flag symptoms requiring immediate emergency care."""
        if not text:
            return False
        emergency_patterns = [
            r"\bchest\s+pain\b",
            r"\bheart\s+attack\b",
            r"\b(shortness\s+of\s+breath|cannot\s+breathe|difficulty\s+breathing|choking)\b",
            r"\b(stroke|slurred\s+speech|facial\s+droop|face\s+droop|paralysis)\b",
            r"\b(coughing\s+blood|vomiting\s+blood|blood\s+in\s+vomit)\b",
            r"\b(unconscious|passed\s+out|blacked\s+out|loss\s+of\s+consciousness)\b",
            r"\b(seizure|convulsion|convulsing)\b",
            r"\b(severe\s+head\s+injury|heavy\s+bleeding|severe\s+burn)\b",
            r"\b(anaphylaxis|swollen\s+throat|throat\s+closing)\b",
            r"\b(suicid|kill\s+myself|end\s+my\s+life)\b"
        ]
        lower_text = text.lower()
        return any(re.search(pattern, lower_text) for pattern in emergency_patterns)

    def chat_response(self, conversation_history: list) -> str:
        """Generates a conversational triage response using full multi-turn chat history."""
        # Primary & backup models on Groq
        models_to_try = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]

        groq_messages = [{"role": "system", "content": self.system_prompt}]
        for msg in conversation_history:
            role = "user" if msg.get("role") == "user" else "assistant"
            groq_messages.append({"role": role, "content": msg.get("content", "")})

        if self.groq_api_key:
            for model_name in models_to_try:
                try:
                    payload = {
                        "model": model_name,
                        "messages": groq_messages,
                        "temperature": 0.2,
                        "max_tokens": 450
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
                    print(f"Groq chat error on {model_name}: {e}")
                    continue

        # Fallback to Google Gemini
        if self.google_api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.google_api_key)
                # Build context
                last_user_query = conversation_history[-1]["content"] if conversation_history else "Help with symptoms"
                full_prompt = f"{self.system_prompt}\n\nPatient Symptoms/Query: {last_user_query}"
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=full_prompt
                )
                return response.text
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    return (
                        "⚠️ **Virtual Assistant is momentarily busy**: High query volume reached. "
                        "Please wait a few moments and ask your question again."
                    )
                return f"⚠️ Unable to analyze symptoms at this moment: {err_str}"

        return "⚠️ Virtual assistant service unavailable. Please check your API configuration."

    def check_symptoms(self, symptoms: str) -> str:
        """Single-turn wrapper for backward compatibility."""
        return self.chat_response([{"role": "user", "content": symptoms}])
