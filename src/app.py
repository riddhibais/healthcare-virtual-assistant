import streamlit as st
import os
from modules.report_explainer import ReportExplainer
from modules.symptom_checker import SymptomChecker
from modules.medicine_info import MedicineInfo

# Force Streamlit reload for Phase 1 OCR updates

# Configure Streamlit page
st.set_page_config(
    page_title="Healthcare Virtual Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize modules
def load_modules():
    return ReportExplainer(), SymptomChecker(), MedicineInfo()

report_engine, symptom_engine, medicine_engine = load_modules()

# Custom CSS for aesthetics
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2e86de;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .disclaimer {
        color: #e74c3c;
        font-size: 0.9em;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏥 AI-Powered Healthcare Virtual Assistant</h1>", unsafe_allow_html=True)
st.write("---")

# Sidebar for navigation
st.sidebar.title("Navigation")
menu = ["📄 Medical Report Explainer", "🩺 Symptom Checker", "💊 Medicine Information"]
choice = st.sidebar.radio("Select a Module:", menu)

# 1. Medical Report Explainer
if choice == "📄 Medical Report Explainer":
    st.header("Medical Report Summarizer & Explainer")
    st.write("Upload your medical report (PDF) and our AI will explain it in simple terms.")
    
    uploaded_file = st.file_uploader("Upload PDF Report", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Analyze Report"):
            with st.spinner("Reading and analyzing your report..."):
                # Save uploaded file temporarily
                temp_path = os.path.join("temp_report.pdf")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process PDF
                result = report_engine.explain_pdf(temp_path)
                
                # Display Result
                st.subheader("Analysis Result:")
                st.write(result)
                
                # Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)

# 2. Symptom Checker
elif choice == "🩺 Symptom Checker":
    st.header("Symptom Checker & Guidance")
    st.write("Describe your symptoms to get a general idea of potential causes and advice.")
    
    symptoms = st.text_area("What are your symptoms?", placeholder="E.g., I have been experiencing a mild fever and headache for 2 days...")
    
    if st.button("Check Symptoms"):
        if symptoms.strip() == "":
            st.warning("Please enter your symptoms.")
        else:
            with st.spinner("Analyzing symptoms..."):
                result = symptom_engine.check_symptoms(symptoms)
                st.subheader("AI Guidance:")
                st.write(result)

# 3. Medicine Information
elif choice == "💊 Medicine Information":
    st.header("Medicine Information Lookup")
    st.write("Ask about any medicine to know its uses, side effects, and precautions.")
    
    medicine_query = st.text_input("Enter medicine name or question:", placeholder="E.g., What is Paracetamol used for?")
    
    if st.button("Search Medicine"):
        if medicine_query.strip() == "":
            st.warning("Please enter a medicine name.")
        else:
            with st.spinner("Searching medical database..."):
                result = medicine_engine.get_info(medicine_query)
                st.subheader("Medicine Details:")
                st.write(result)
