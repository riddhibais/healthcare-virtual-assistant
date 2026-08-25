import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class SymptomChecker:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            temperature=0.0, 
            model="gemini-1.5-flash",
            google_api_key=api_key
        )
        
        system_prompt = (
            "You are a helpful AI health assistant. "
            "A user is describing their symptoms. "
            "Provide a very direct, concise answer. Do NOT use <think> tags, internal monologues, or long explanations. "
            "Provide general information about what these symptoms might indicate, and suggest basic home care or when to see a doctor. "
            "DO NOT diagnose the patient. "
            "ALWAYS end your response with this disclaimer: '*Disclaimer: This is for informational purposes only and does not constitute medical advice. Please consult a doctor for an accurate diagnosis.*'"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{symptoms}"),
        ])
        
        self.chain = self.prompt | self.llm

    def check_symptoms(self, symptoms: str):
        try:
            response = self.chain.invoke({"symptoms": symptoms})
            clean_text = response.content
            
            if "</think>" in clean_text:
                clean_text = clean_text.split("</think>")[-1].strip()
            elif "<think>" in clean_text:
                return "⚠️ The AI's thought process was too long and it ran out of memory before giving the final answer. Please try again."
                
            import re
            clean_text = re.sub(r'<think>.*?</think>', '', clean_text, flags=re.DOTALL).strip()
            return clean_text
        except Exception as e:
            return f"Error analyzing symptoms: {str(e)}"
