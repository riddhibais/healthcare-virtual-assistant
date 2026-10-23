import os
import sys
import io
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# DYNAMIC MODULE PATH & IMPORT HANDLING
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(CURRENT_DIR, "modules")

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

try:
    from modules.report_explainer import ReportExplainer
    from modules.symptom_checker import SymptomChecker
    from modules.medicine_info import MedicineInfo
except ImportError:
    from report_explainer import ReportExplainer
    from symptom_checker import SymptomChecker
    from medicine_info import MedicineInfo

# Voice Dictation & Audio Transcription Libraries
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False

def transcribe_audio_bytes(audio_bytes):
    """Transcribe raw audio bytes from st.audio_input using SpeechRecognition."""
    if not HAS_SPEECH_RECOGNITION or not audio_bytes:
        return "⚠️ SpeechRecognition module is not installed."
    try:
        r = sr.Recognizer()
        r.energy_threshold = 250
        r.dynamic_energy_threshold = True
        audio_stream = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_stream) as source:
            audio_data = r.record(source)
        return r.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "⚠️ Audio was recorded, but no clear speech was recognized. Please speak closer to your microphone."
    except sr.RequestError as e:
        return f"⚠️ Google Speech service unreachable: {e}"
    except Exception as e:
        return f"⚠️ Audio processing notice: {e}"

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Healthcare Virtual Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for main header, disclaimer text, badges, and response cards
st.markdown("""
<style>
    /* Main Header Styling */
    .main-title {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0F52BA 0%, #1E88E5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        font-size: 1.05rem;
        color: #5A6A85;
        margin-bottom: 1.8rem;
    }

    /* Disclaimer Styling */
    .disclaimer {
        background-color: #FFF8E1;
        border-left: 5px solid #FFC107;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 0.88rem;
        color: #5D4037;
        margin-top: 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    
    .disclaimer-title {
        font-weight: 700;
        color: #B78103;
        margin-bottom: 4px;
    }

    /* Section Cards */
    .content-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 22px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }

    /* Badge & Tag Styling */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-high { background-color: #FFEBEE; color: #C62828; }
    .badge-low { background-color: #FFF3E0; color: #EF6C00; }
    .badge-normal { background-color: #E8F5E9; color: #2E7D32; }

    /* Button hover tweaks */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Engine Initialization (Cached for optimal performance)
@st.cache_resource
def load_engines():
    return ReportExplainer(), SymptomChecker(), MedicineInfo()

report_engine, symptom_engine, medicine_engine = load_engines()

# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/hospital.png", width=70)
    st.title("CareAssistant AI")
    st.caption("Your 24/7 Virtual Health Companion")
    st.divider()

    st.subheader("Navigation")
    module_choice = st.sidebar.radio(
        "Select a Module:",
        options=[
            "📄 Medical Report Explainer",
            "🩺 Symptom Checker",
            "💊 Medicine Information"
        ],
        index=0
    )

    st.divider()
    st.markdown("### 📊 Assistant Info")
    st.info("💡 **Tip:** Use the microphone recorder in the Symptom Checker tab for quick voice dictation!")
    st.caption("v2.5 • Clinical Decision Support System")

# Top Header Block
st.markdown('<div class="main-title">🏥 Healthcare Virtual Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Clinical Guidance • Report Parsing • Symptom Triage • Medication Database</div>', unsafe_allow_html=True)

# ==========================================
# 3. MODULE BREAKDOWN & WORKFLOWS
# ==========================================

# ------------------------------------------
# MODULE 1: 📄 Medical Report Explainer
# ------------------------------------------
if module_choice == "📄 Medical Report Explainer":
    st.subheader("📄 Medical Report Explainer")
    st.markdown("Upload your clinical laboratory report (PDF format) to receive a simplified breakdown, out-of-range flag analysis, and medical summaries.")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a Medical PDF Report",
            type=["pdf"],
            help="Upload lab reports such as Complete Blood Count (CBC), Lipid Panel, Metabolic Panel, or Thyroid Profile."
        )

    with col2:
        st.markdown("##### 🧪 Don't have a report?")
        if st.button("Generate & Test Sample Blood Report PDF", type="secondary"):
            sample_path = os.path.join(CURRENT_DIR, "sample_blood_report.pdf")
            if not os.path.exists(sample_path):
                try:
                    from create_sample_report import generate_sample_blood_report
                    generate_sample_blood_report(sample_path)
                except ImportError:
                    st.info("Sample generator script ready.")

            if os.path.exists(sample_path):
                with open(sample_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Sample PDF for Testing",
                        data=f,
                        file_name="sample_blood_report.pdf",
                        mime="application/pdf"
                    )
                st.success("Sample PDF ready! Download and upload it above.")

    if uploaded_file is not None:
        st.success(f"File uploaded: **{uploaded_file.name}** ({round(uploaded_file.size / 1024, 1)} KB)")

        if st.button("🔬 Analyze Report", type="primary", use_container_width=True):
            temp_path = os.path.join(CURRENT_DIR, "temp_report.pdf")
            try:
                # 1. Save uploaded PDF temporarily to disk
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.spinner("Parsing medical PDF, evaluating lab markers, and generating plain-English insights..."):
                    # 2. Call backend report_engine.explain_pdf()
                    result = report_engine.explain_pdf(temp_path)

                # 3. Render analysis result under subheader
                if result.get("success"):
                    st.divider()
                    st.subheader("📊 Analysis Results & Lab Findings")
                    
                    # Overall Summary Callout
                    st.info(f"**Overall Summary:** {result['summary']}")

                    # Detected Metrics Table
                    metrics = result.get("metrics", [])
                    if metrics:
                        st.markdown("#### 🔬 Detailed Lab Parameter Breakdown")
                        
                        table_data = []
                        for m in metrics:
                            table_data.append({
                                "Lab Metric": m["name"],
                                "Observed Value": f"{m['value']} {m['unit']}",
                                "Reference Range": m["reference_range"],
                                "Status": m["status"],
                                "Clinical Note": m["interpretation"]
                            })
                        st.dataframe(table_data, use_container_width=True)
                    else:
                        st.warning("No standard numeric lab values were automatically parsed. Detailed text summary below:")

                    # Plain-English Translation Section
                    st.markdown("#### 🗣️ Plain-English Translation")
                    for line in result.get("plain_english_translation", []):
                        st.markdown(line)

                    # Actionable Recommendations
                    st.markdown("#### 📋 Recommended Next Steps")
                    for rec in result.get("recommendations", []):
                        st.markdown(f"• {rec}")

                    with st.expander("🔍 View Extracted PDF Raw Text"):
                        st.text(result.get("raw_snippet", ""))

                else:
                    st.error(f"Analysis Failed: {result.get('error', 'Unknown error occurred.')}")

            finally:
                # 4. Safely cleanup and delete temporary file from system
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception as cleanup_err:
                        st.warning(f"Note: Temporary file cleanup alert: {cleanup_err}")

# ------------------------------------------
# MODULE 2: 🩺 Symptom Checker
# ------------------------------------------
elif module_choice == "🩺 Symptom Checker":
    st.subheader("🩺 AI Symptom Checker & Voice Triage")
    st.markdown("Describe what symptoms or discomfort you are experiencing. You can type manually, speak into the **Microphone**, or use **Live Dictation**.")

    # Session state initialization for text area
    if "symptoms_text_area" not in st.session_state:
        st.session_state["symptoms_text_area"] = ""

    # Primary Voice Input: Streamlit Native Audio Recorder (Guaranteed browser mic access)
    st.markdown("##### 🎙️ Voice Input (Click the red circle to record & speak)")
    audio_clip = st.audio_input("Record your symptoms", key="symptom_audio_clip")
    if audio_clip is not None:
        raw_bytes = audio_clip.getvalue()
        audio_id = f"audio_{len(raw_bytes)}_{raw_bytes[:32]}"
        if st.session_state.get("_last_audio_id") != audio_id:
            st.session_state["_last_audio_id"] = audio_id
            with st.spinner("🎧 Transcribing your voice recording with Google Speech..."):
                clip_text = transcribe_audio_bytes(raw_bytes)
                if clip_text and not clip_text.startswith("⚠️"):
                    curr = st.session_state.get("symptoms_text_area", "")
                    if curr.strip():
                        st.session_state["symptoms_text_area"] = curr.strip() + " " + clip_text
                    else:
                        st.session_state["symptoms_text_area"] = clip_text
                    st.toast(f"Spoken text captured: {clip_text}", icon="🎙️")
                    st.rerun()
                elif clip_text:
                    st.warning(clip_text)

    # Secondary Voice Tool: Live Web Speech Popup Tool
    html_path = os.path.join(CURRENT_DIR, "components.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=95)

    # Quick Symptom Templates
    st.markdown("**⚡ Quick Preset Symptoms (Click to test):**")
    qcols = st.columns(4)
    if qcols[0].button("🤒 Fever & Sore Throat", use_container_width=True):
        st.session_state["symptoms_text_area"] = "I have had a high fever (101 F), severe sore throat, and body chills for the past 2 days."
        st.rerun()
    if qcols[1].button("🤧 Cough & Congestion", use_container_width=True):
        st.session_state["symptoms_text_area"] = "Persistent dry cough, nasal congestion, headache, and runny nose for 4 days."
        st.rerun()
    if qcols[2].button("🤕 Migraine & Nausea", use_container_width=True):
        st.session_state["symptoms_text_area"] = "Severe throbbing headache on one side of my head, sensitivity to light, and mild nausea."
        st.rerun()
    if qcols[3].button("🚨 Chest Pain & Shortness", use_container_width=True):
        st.session_state["symptoms_text_area"] = "Sudden tight chest pain radiating to left arm with acute shortness of breath."
        st.rerun()

    # Text area for symptom input (populated automatically from voice or manual typing)
    symptoms_input = st.text_area(
        "Describe your symptoms in detail:",
        key="symptoms_text_area",
        height=130,
        placeholder="E.g., I have had a sore throat, mild fever, and dry cough for the past 2 days...",
        help="Include duration, severity, and any associated discomfort."
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        check_btn = st.button("🩺 Check Symptoms", type="primary", use_container_width=True)
    with col2:
        if st.button("🧹 Clear Input", type="secondary"):
            st.session_state["symptoms_text_area"] = ""
            st.session_state["_last_audio_id"] = None
            st.rerun()

    if check_btn:
        if not symptoms_input.strip():
            st.warning("⚠️ Please enter or dictate your symptoms before submitting.")
        else:
            with st.spinner("Analyzing symptoms and evaluating emergency red flags..."):
                triage_res = symptom_engine.check_symptoms(symptoms_input)

            if triage_res.get("success"):
                st.divider()
                st.subheader("📋 Clinical Triage Assessment")

                # Urgency Level Header Box
                urgency = triage_res["urgency_level"]
                color = triage_res["urgency_color"]
                bg = triage_res["badge_bg"]

                st.markdown(
                    f"""
                    <div style="background-color: {bg}; border-left: 6px solid {color}; padding: 16px 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="margin:0; color: {color}; font-size: 1.3rem;">Urgency Level: {urgency}</h3>
                        <p style="margin: 6px 0 0 0; color: #333; font-weight: 500;">{triage_res['action_required']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("#### 🩺 Recommended Medical Specialist")
                    st.info(f"**{triage_res['specialist']}**")

                    st.markdown("#### 🔍 Potential Considerations")
                    for cond in triage_res["potential_conditions"]:
                        st.markdown(f"• {cond}")

                with col_b:
                    st.markdown("#### ❓ Questions to Ask Your Doctor")
                    for q in triage_res["questions_for_doctor"]:
                        st.markdown(f"• {q}")

                    st.markdown("#### 🚨 Warning Red Flags")
                    for sign in triage_res["warning_signs"]:
                        st.warning(sign)

# ------------------------------------------
# MODULE 3: 💊 Medicine Information
# ------------------------------------------
elif module_choice == "💊 Medicine Information":
    st.subheader("💊 Medicine Information & Safety Lookup")
    st.markdown("Search for prescription drugs or over-the-counter medications to view uses, standard dosage guidelines, side effects, and drug interactions.")

    # Quick Select Buttons
    st.markdown("**Quick Select Popular Medications:**")
    quick_meds = ["Paracetamol", "Ibuprofen", "Amoxicillin", "Metformin", "Atorvastatin", "Lisinopril", "Omeprazole", "Cetirizine"]
    
    selected_quick = None
    cols = st.columns(8)
    for idx, med in enumerate(quick_meds):
        if cols[idx].button(med, key=f"btn_{med}"):
            selected_quick = med

    # Query Input Field
    default_val = selected_quick if selected_quick else ""
    search_query = st.text_input(
        "Enter Medicine Name or Medical Question:",
        value=default_val,
        placeholder="E.g., Paracetamol, Amoxicillin, or 'What is Ibuprofen used for?'",
        help="Type any drug brand or generic name."
    )

    search_btn = st.button("🔍 Search Medicine", type="primary")

    if search_btn or selected_quick:
        query_to_search = search_query if search_query else selected_quick
        if not query_to_search or not query_to_search.strip():
            st.warning("⚠️ Please enter a medicine name to search.")
        else:
            with st.spinner(f"Retrieving pharmacological information for '{query_to_search}'..."):
                med_res = medicine_engine.get_info(query_to_search)

            if med_res.get("success"):
                data = med_res["data"]
                st.divider()
                st.subheader(f"💊 Medication Details: {data['generic_name']}")

                # Category & Brands Header
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Therapeutic Category:** `{data['category']}`")
                with col2:
                    brands_str = ", ".join(data.get("brand_names", []))
                    st.markdown(f"**Common Brand Names:** `{brands_str}`")

                st.markdown("---")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 🎯 Primary Uses & Indications")
                    for use in data.get("uses", []):
                        st.markdown(f"• {use}")

                    st.markdown("#### 📐 Standard Dosage Guidelines")
                    st.info(data.get("dosage", "Consult doctor for exact dosing."))

                    st.markdown("#### ⚠️ Precautions & Warnings")
                    st.warning(data.get("precautions", "Follow physician instructions."))

                with c2:
                    st.markdown("#### 🩺 Common Side Effects")
                    for se in data.get("common_side_effects", []):
                        st.markdown(f"• {se}")

                    st.markdown("#### 🚨 Serious Side Effects (Seek Immediate Care)")
                    for sse in data.get("serious_side_effects", []):
                        st.markdown(f"• **{sse}**")

                    st.markdown("#### ⚡ Known Drug Interactions")
                    for inter in data.get("interactions", []):
                        st.markdown(f"• {inter}")

# ==========================================
# 4. GLOBAL DISCLAIMER FOOTER
# ==========================================
st.markdown("""
<div class="disclaimer">
    <div class="disclaimer-title">⚠️ MEDICAL DISCLAIMER</div>
    This Healthcare Virtual Assistant tool is designed strictly for informational and educational decision-support purposes. 
    It is <b>NOT</b> a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the direct guidance of your physician or qualified health provider with any questions regarding a medical condition or symptoms. 
    If you think you may have a medical emergency, call your local emergency services (911) immediately.
</div>
""", unsafe_allow_html=True)