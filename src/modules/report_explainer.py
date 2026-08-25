import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ReportExplainer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            temperature=0.0,
            model="gemini-1.5-flash",
            google_api_key=api_key,
            max_tokens=4096
        )
        
        system_prompt = (
            "You are a helpful and highly empathetic medical assistant. "
            "A user has provided a medical report text. "
            "Your task is to summarize the report in EXTREMELY SIMPLE language for a layman with no medical background. "
            "You MUST format your response exactly like this:\n\n"
            "### 📝 Simple Summary & Risks\n"
            "(Write a few lines explaining exactly WHAT the disease or problem is, WHY it happened, and the potential RISKS if ignored. Use simple analogies if needed. Talk like a caring friend.)\n\n"
            "### ⚠️ Abnormal Findings\n"
            "(List the abnormal values in a simple table or bullet points, explaining what each means simply.)\n\n"
            "ALWAYS include this disclaimer at the end: '*Disclaimer: I am an AI, not a doctor. Please consult a qualified healthcare professional before making any medical decisions based on this report.*'"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Here is the medical report text:\n\n{report_text}"),
        ])
        
        self.chain = self.prompt | self.llm

    def explain_pdf(self, pdf_path: str):
        try:
            loader = PyMuPDFLoader(pdf_path)
            documents = loader.load()
            report_text = "\n".join([doc.page_content for doc in documents])
            
            # If standard extraction fails (likely a scanned PDF), fallback to OCR
            if not report_text.strip():
                try:
                    import fitz
                    import pytesseract
                    from PIL import Image
                    
                    doc = fitz.open(pdf_path)
                    ocr_text = ""
                    for page in doc:
                        # Render page to an image
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x zoom for better OCR quality
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        # Run OCR on the image
                        ocr_text += pytesseract.image_to_string(img)
                    
                    report_text = ocr_text
                    
                    if not report_text.strip():
                        return "⚠️ **OCR Failed.** Could not read the scanned document. Please ensure the image is clear."
                except ImportError:
                    return "⚠️ **OCR Dependencies Missing.** Please run `pip install pytesseract Pillow`."
                except Exception as e:
                    return f"⚠️ **OCR Error:** You need to install the **Tesseract OCR** software on your Windows PC for this to work.\n\n1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n2. Install it.\n3. Restart your terminal.\n\n*Technical detail: {str(e)}*"
            
            response = self.chain.invoke({"report_text": report_text})
            clean_text = response.content
            
            # Robustly remove <think> tags even if they are large
            if "</think>" in clean_text:
                clean_text = clean_text.split("</think>")[-1].strip()
            elif "<think>" in clean_text:
                # Means it hit token limit before finishing thoughts
                return "⚠️ The AI's thought process was too long and it ran out of memory before giving the final answer. Please try again with a shorter report."
            
            # Fallback regex just in case there are multiple tags
            import re
            clean_text = re.sub(r'<think>.*?</think>', '', clean_text, flags=re.DOTALL).strip()
            
            return clean_text
        except Exception as e:
            return f"Error processing report: {str(e)}"
