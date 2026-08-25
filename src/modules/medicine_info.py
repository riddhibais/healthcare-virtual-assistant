import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class MedicineInfo:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            temperature=0, 
            model="gemini-1.5-flash",
            google_api_key=api_key
        )
        
        system_prompt = (
            "You are a helpful pharmacist AI. "
            "A user is asking about a specific medicine. "
            "Provide ONLY a very short and basic summary (maximum 3-4 lines). "
            "Provide a very direct, concise answer. Do NOT use <think> tags, internal monologues, or long explanations. "
            "Just mention what it is used for and 1 or 2 main side effects. "
            "Do NOT provide long lists or excessive details. Keep it extremely brief. "
            "ALWAYS end your response with: '*Disclaimer: Do not take any medication without consulting your doctor first.*'"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{medicine_query}"),
        ])
        
        self.chain = self.prompt | self.llm

    def get_info(self, medicine_query: str):
        try:
            response = self.chain.invoke({"medicine_query": medicine_query})
            clean_text = response.content
            
            if "</think>" in clean_text:
                clean_text = clean_text.split("</think>")[-1].strip()
            elif "<think>" in clean_text:
                return "⚠️ The AI's thought process was too long and it ran out of memory before giving the final answer. Please try again."
                
            import re
            clean_text = re.sub(r'<think>.*?</think>', '', clean_text, flags=re.DOTALL).strip()
            return clean_text
        except Exception as e:
            return f"Error retrieving medicine information: {str(e)}"
