import os
import sys

# Ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.report_explainer import ReportExplainer
from modules.symptom_checker import SymptomChecker
from modules.medicine_info import MedicineInfo

def main():
    print("\n" + "="*50)
    print("🏥 HEALTHCARE VIRTUAL ASSISTANT (BACKEND TEST)")
    print("="*50)
    
    print("\nInitializing AI Models (Please wait...).")
    try:
        report_engine = ReportExplainer()
        symptom_engine = SymptomChecker()
        medicine_engine = MedicineInfo()
    except Exception as e:
        print(f"Failed to initialize models. Check your API key. Error: {e}")
        return

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Medical Report Explainer (PDF)")
        print("2. Symptom Checker (Chat)")
        print("3. Medicine Information")
        print("4. Exit")
        
        choice = input("\nSelect a module (1-4): ").strip()
        
        if choice == '1':
            print("\n--- Medical Report Explainer ---")
            pdf_path = input("Enter the full path to the PDF report (or type 'cancel'): ").strip()
            if pdf_path.lower() != 'cancel':
                # Remove quotes if user dragged and dropped the file
                pdf_path = pdf_path.strip('"\'')
                if os.path.exists(pdf_path):
                    print("\nAnalyzing report... (this might take a few seconds)")
                    result = report_engine.explain_pdf(pdf_path)
                    print("\n[AI RESPONSE]")
                    print(result)
                else:
                    print("File not found! Please check the path.")
                    
        elif choice == '2':
            print("\n--- Symptom Checker ---")
            print("Type 'back' to return to the main menu.")
            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() == 'back':
                    break
                if user_input:
                    print("AI is thinking...")
                    result = symptom_engine.check_symptoms(user_input)
                    print(f"\nAI Doctor: {result}")
                    
        elif choice == '3':
            print("\n--- Medicine Information ---")
            print("Type 'back' to return to the main menu.")
            while True:
                user_input = input("\nEnter medicine name: ").strip()
                if user_input.lower() == 'back':
                    break
                if user_input:
                    print("Searching database...")
                    result = medicine_engine.get_info(user_input)
                    print(f"\n[AI RESPONSE]\n{result}")
                    
        elif choice == '4':
            print("\nExiting. Have a healthy day!")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
