
import tempfile
from pathlib import Path

import importlib

try:
    st = importlib.import_module("streamlit")
except ImportError as exc:
    raise SystemExit(
        "Streamlit is required to run this application. Install it in the "
        "active Python environment with: python -m pip install streamlit"
    ) from exc

from src.modules.report_explainer import ReportExplainer
from src.modules.symptom_checker import SymptomChecker
from src.modules.medicine_info import MedicineInfo


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Healthcare Virtual Assistant",
    page_icon="🏥",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            color: #2e86de;
            font-family: Arial, sans-serif;
        }
        .disclaimer {
            color: #e74c3c;
            font-size: 0.9em;
            font-style: italic;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 class='main-title'>Healthcare Virtual Assistant</h1>",
    unsafe_allow_html=True,
)

st.caption(
    "General health information only. This application does not "
    "replace a qualified healthcare professional."
)
st.divider()


# --------------------------------------------------
# Initialize modules once per Streamlit session
# --------------------------------------------------
@st.cache_resource
def load_modules():
    return ReportExplainer(), SymptomChecker(), MedicineInfo()


try:
    report_engine, symptom_engine, medicine_engine = load_modules()
except Exception as exc:
    st.error(f"Unable to initialize the application modules: {exc}")
    st.stop()


# --------------------------------------------------
# Navigation
# --------------------------------------------------
st.sidebar.title("Navigation")

choice = st.sidebar.radio(
    "Select a module:",
    [
        "Medical Report Explainer",
        "Symptom Checker",
        "Medicine Information",
    ],
)


# --------------------------------------------------
# 1. Medical Report Explainer
# --------------------------------------------------
if choice == "Medical Report Explainer":
    st.header("Medical Report Explainer")
    st.write(
        "Upload a PDF report to extract its text and request a "
        "plain-language explanation."
    )

    uploaded_file = st.file_uploader(
        "Upload your medical report",
        type=["pdf"],
        key="medical_report_pdf",
    )

    if uploaded_file is not None:
        if st.button("Analyze Report", type="primary"):
            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf",
                    delete=False,
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = Path(temp_file.name)

                with st.spinner("Reading and analyzing the report..."):
                    result = report_engine.explain_pdf(str(temp_path))

                st.subheader("Analysis Result")
                st.write(result)

            except Exception as exc:
                st.error(f"Could not process the PDF: {exc}")

            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)


# --------------------------------------------------
# 2. Symptom Checker
# --------------------------------------------------
elif choice == "Symptom Checker":
    st.header("Symptom Checker")
    st.write(
        "Describe your symptoms to request general health information. "
        "This tool cannot diagnose a medical condition."
    )

    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder=(
            "For example: I have had a headache and felt tired "
            "since yesterday."
        ),
        max_chars=3000,
    )

    if st.button("Check Symptoms", type="primary"):
        if not symptoms.strip():
            st.warning("Please describe your symptoms first.")
        else:
            with st.spinner("Checking approved medical references..."):
                try:
                    result = symptom_engine.check_symptoms(symptoms)
                    st.subheader("General Guidance")
                    st.write(result)
                except Exception as exc:
                    st.error(f"Unable to check symptoms: {exc}")

    st.info(
        "If you think you may be experiencing a medical emergency, "
        "seek emergency medical care rather than relying on this tool."
    )


# --------------------------------------------------
# 3. Medicine Information
# --------------------------------------------------
elif choice == "Medicine Information":
    st.header("Medicine Information")
    st.write(
        "Ask a question about a medicine. Responses should be based "
        "on approved medical references."
    )

    medicine_query = st.text_input(
        "Medicine name or question",
        placeholder="For example: What information is available about paracetamol?",
        max_chars=500,
    )

    if st.button("Search Medicine", type="primary"):
        if not medicine_query.strip():
            st.warning("Please enter a medicine name or question.")
        else:
            with st.spinner("Searching approved medical references..."):
                try:
                    result = medicine_engine.get_info(medicine_query)
                    st.subheader("Medicine Information")
                    st.write(result)
                except Exception as exc:
                    st.error(f"Unable to retrieve medicine information: {exc}")


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption(
    "Important: AI-generated information may be incomplete. "
    "Consult a qualified healthcare professional for medical decisions."
)
