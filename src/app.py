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

# Cached on-demand module initializers (prevents startup freezing and reloads)
@st.cache_resource(show_spinner="Initializing Medical Report AI Engine...")
def get_report_engine():
    return ReportExplainer()

@st.cache_resource(show_spinner="Initializing Symptom Checker AI Engine...")
def get_symptom_engine():
    return SymptomChecker()

@st.cache_resource(show_spinner="Loading Clinical Medicine Knowledge Base (ChromaDB)...")
def get_medicine_engine():
    return MedicineInfo()

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
    report_engine = get_report_engine()
    st.header("📄 Medical Report Summarizer & Lab Triage")
    st.write("Upload your lab report (**PDF, JPG, PNG**) or type your test numbers directly. The assistant will read only your report and give a simple, real explanation.")

    uploaded_file = st.file_uploader(
        "Upload Lab Report (PDF, JPG, PNG, JPEG)", 
        type=["pdf", "png", "jpg", "jpeg"],
        help="Upload a digital PDF from your diagnostic lab or a clear photo of your test paper."
    )

    with st.expander("📝 Or Type / Paste Lab Report Text Directly"):
        pasted_text = st.text_area(
            "Enter report parameters and numbers here:", 
            placeholder="E.g., Hemoglobin: 10.2 g/dL, WBC: 12000, Fasting Blood Sugar: 140 mg/dL...",
            height=120
        )
        paste_submit = st.button("🔍 Analyze Entered Text", type="secondary")

    if uploaded_file is not None:
        if st.button("🔍 Analyze Uploaded Report", type="primary", use_container_width=True):
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            temp_path = os.path.join(f"temp_report{file_ext}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("Reading and analyzing your medical report..."):
                if file_ext == ".pdf":
                    res = report_engine.explain_pdf(temp_path)
                else:
                    res = report_engine.explain_image(temp_path)

                st.session_state["report_result"] = res

            if os.path.exists(temp_path):
                os.remove(temp_path)
    elif paste_submit and pasted_text.strip():
        with st.spinner("Analyzing your report values..."):
            st.session_state["report_result"] = report_engine.explain_text(pasted_text.strip())

    # Display Result
    if st.session_state.get("report_result"):
        st.markdown("---")
        st.subheader("📋 Lab Report Explanation")
        st.markdown(st.session_state["report_result"])

# 2. Symptom Checker & Virtual Health Assistant
elif choice == "🩺 Symptom Checker":
    symptom_engine = get_symptom_engine()
    
    col_head, col_act = st.columns([3, 1])
    with col_head:
        st.header("🩺 AI Health Assistant & Symptom Triage")
        st.write("Have a conversation with your virtual health assistant. Describe what you're feeling, answer clarifying questions, and receive detailed clinical triage guidance.")
    with col_act:
        st.write("")
        if st.button("🗑️ Reset Chat", use_container_width=True):
            st.session_state["symptom_messages"] = []
            st.session_state["emergency_detected"] = False
            st.rerun()

    if "symptom_messages" not in st.session_state or not st.session_state["symptom_messages"]:
        st.session_state["symptom_messages"] = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Hello! I am your AI Health Assistant.**\n\n"
                    "I am here to listen and help you understand your symptoms, what might be causing them, and what practical steps you can take.\n\n"
                    "You can type your symptoms below or click one of the quick starters below to begin."
                )
            }
        ]

    if "emergency_detected" not in st.session_state:
        st.session_state["emergency_detected"] = False

    # Emergency SOS Banner if triggered
    if st.session_state["emergency_detected"]:
        st.error(
            "🚨 **CRITICAL MEDICAL ALERT: Urgent / Severe Symptoms Detected!**\n\n"
            "Your symptoms may indicate an emergency requiring immediate in-person attention:\n"
            "* 🚑 **Emergency Ambulances**: Call **108** (India) or **911** (US) immediately.\n"
            "* 🏥 **Action**: Please visit the nearest Emergency Room (ER) or hospital without delay. Do not drive yourself."
        )

    # Quick topic buttons (chips)
    st.caption("Common Symptom Starters:")
    chip_cols = st.columns(5)
    selected_chip = None
    if chip_cols[0].button("🌡️ Fever & Body Ache", use_container_width=True):
        selected_chip = "I have a fever of 101°F with body aches and shivering for the past 2 days."
    if chip_cols[1].button("🤕 Migraine & Eyes", use_container_width=True):
        selected_chip = "I have a throbbing headache on one side of my head and sensitivity to light."
    if chip_cols[2].button("🤢 Stomach Cramps", use_container_width=True):
        selected_chip = "I have sharp stomach cramps, bloating, and mild nausea after eating."
    if chip_cols[3].button("🤧 Cough & Throat", use_container_width=True):
        selected_chip = "I have a dry cough, painful throat when swallowing, and mild runny nose."
    if chip_cols[4].button("⚡ Fatigue & Dizzy", use_container_width=True):
        selected_chip = "I feel unusually exhausted, weak, and dizzy when standing up quickly."

    # Display Chat History
    for msg in st.session_state["symptom_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input & Chip Trigger
    user_prompt = st.chat_input("Describe your symptoms or reply to the assistant...")

    query_to_send = selected_chip if selected_chip else user_prompt

    if query_to_send:
        # Check emergency keywords
        if symptom_engine.check_emergency(query_to_send):
            st.session_state["emergency_detected"] = True

        # Append user message
        st.session_state["symptom_messages"].append({"role": "user", "content": query_to_send})
        with st.chat_message("user"):
            st.markdown(query_to_send)

        # Generate Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your symptoms and clinical possibilities..."):
                reply = symptom_engine.chat_response(st.session_state["symptom_messages"])
                st.markdown(reply)

        st.session_state["symptom_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

# 3. Medicine Information Lookup
elif choice == "💊 Medicine Information":
    medicine_engine = get_medicine_engine()
    st.header("💊 Medicine Information Lookup")
    st.write("Search any medicine or brand name worldwide — learn about uses, dosage, side effects, and precautions in simple steps.")
    
    if "med_query" not in st.session_state:
        st.session_state["med_query"] = ""
    if "searched_med" not in st.session_state:
        st.session_state["searched_med"] = ""
    if "current_medicine_result" not in st.session_state:
        st.session_state["current_medicine_result"] = ""

    st.caption("Quick Searches:")
    cols = st.columns(5)
    quick_selected = None
    if cols[0].button("Allegra", use_container_width=True):
        quick_selected = "Allegra"
    if cols[1].button("Dolo 650", use_container_width=True):
        quick_selected = "Dolo 650"
    if cols[2].button("Combiflam", use_container_width=True):
        quick_selected = "Combiflam"
    if cols[3].button("Augmentin", use_container_width=True):
        quick_selected = "Augmentin"
    if cols[4].button("Meftal Spas", use_container_width=True):
        quick_selected = "Meftal Spas"

    if quick_selected:
        st.session_state["med_query"] = quick_selected
        st.session_state["searched_med"] = quick_selected
        with st.spinner(f"Looking up clinical details for '{quick_selected}'..."):
            st.session_state["current_medicine_result"] = medicine_engine.get_info(quick_selected)

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        user_query = st.text_input(
            "Enter medicine name or question:",
            key="med_query",
            placeholder="E.g., Allegra, Dolo 650, Combiflam, Augmentin, Meftal Spas, Pan 40...",
            label_visibility="visible"
        )
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)

    clean_target = user_query.strip() if user_query else ""

    # Triggers on single Enter press or button click
    should_search = False
    if search_clicked:
        should_search = True
    elif clean_target and clean_target != st.session_state.get("searched_med", ""):
        should_search = True

    if should_search:
        if not clean_target:
            st.warning("⚠️ Please enter a medicine name to search.")
        else:
            with st.spinner(f"Looking up clinical details for '{clean_target}'..."):
                result = medicine_engine.get_info(clean_target)
                st.session_state["searched_med"] = clean_target
                st.session_state["current_medicine_result"] = result

    if st.session_state.get("current_medicine_result"):
        res = st.session_state["current_medicine_result"]
        st.markdown("---")
        if res.startswith("❌"):
            st.warning(res)
        else:
            st.markdown(res)
