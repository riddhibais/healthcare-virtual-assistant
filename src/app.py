import streamlit as st
import os
import io
from modules.report_explainer import ReportExplainer
from modules.symptom_checker import SymptomChecker
from modules.medicine_info import MedicineInfo

# Configure Streamlit page
st.set_page_config(
    page_title="Healthcare Virtual Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Inject Modern Healthcare Design Theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Font (Preserves Streamlit Material Icons) */
html, body, p, h1, h2, h3, h4, h5, h6, span, button, input, textarea, label {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

[data-testid="stIconMaterial"], .material-icons, .material-symbols-rounded, [data-testid="stSidebarCollapseButton"] * {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}

/* Main App Background & Typography */
[data-testid="stAppViewContainer"] {
    background-color: #F8FAFC !important;
}

[data-testid="stMainBlockContainer"],
[data-testid="stMain"],
[data-testid="stMain"] .stMarkdown,
[data-testid="stMain"] p,
[data-testid="stMain"] span,
[data-testid="stMain"] li,
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] h5,
[data-testid="stMain"] h6 {
    color: #0F172A !important;
}

/* Chat Message Styling */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04) !important;
}

[data-testid="stChatMessage"] * {
    color: #0F172A !important;
}

/* User Message Bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, #EFF6FF 0%, #E0EEFD 100%) !important;
    border: 1.5px solid #BFDBFE !important;
}

/* Bottom Chat Input Bar */
[data-testid="stBottom"] {
    background: #F8FAFC !important;
    border-top: 1px solid #E2E8F0 !important;
    padding: 10px 0 16px 0 !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06) !important;
    padding: 2px 6px !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    color: #0F172A !important;
    font-size: 14.5px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94A3B8 !important;
}

[data-testid="stChatInput"] button {
    color: #2563EB !important;
}

/* Input Fields & Textareas */
.stTextInput input, .stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

/* Header */
[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Sidebar Dark Navy Styling */
[data-testid="stSidebar"] {
    background-color: #0E1726 !important;
    border-right: 1px solid #1E293B !important;
}

[data-testid="stSidebar"] * {
    color: #F1F5F9 !important;
}

/* Brand Header */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 4px 22px 4px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 24px;
}

.brand-icon-box {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45);
}

.brand-title {
    font-size: 18px;
    font-weight: 800;
    color: #FFFFFF !important;
    line-height: 1.1;
    letter-spacing: -0.3px;
}

.brand-subtitle {
    font-size: 13px;
    font-weight: 500;
    color: #94A3B8 !important;
    margin-top: 3px;
}

/* Sidebar Radio Navigation Pill Items */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 8px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent !important;
    padding: 12px 16px !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
    color: #94A3B8 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #1E293B !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked),
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background: #1E293B !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
}

/* Hide native radio circles */
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Top Greeting */
.top-greeting {
    text-align: right;
    margin-bottom: 6px;
}
.greeting-hello {
    font-size: 14px;
    font-weight: 700;
    color: #0F172A;
}
.greeting-sub {
    font-size: 13px;
    color: #64748B;
}

/* Hero Welcome Card */
.hero-card {
    background: linear-gradient(135deg, #F0F6FF 0%, #E2EEFD 100%);
    border: 1.5px solid #BFDBFE;
    border-radius: 20px;
    padding: 34px 40px;
    margin-bottom: 28px;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
}

.hero-welcome-badge {
    font-size: 15px;
    font-weight: 500;
    color: #475569;
    margin-bottom: 6px;
}

.hero-title {
    font-size: 36px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.6px;
    margin: 0 0 14px 0;
    line-height: 1.15;
}

.hero-subtitle {
    font-size: 15px;
    color: #475569;
    line-height: 1.5;
    max-width: 520px;
    margin: 0;
}

/* 3 Feature Cards */
.feature-card {
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 18px;
    padding: 28px 24px 20px 24px;
    box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
    height: 250px;
}

.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.1);
}

.icon-badge {
    width: 54px;
    height: 54px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 18px;
}

.badge-blue {
    background: #EFF6FF;
    color: #2563EB;
}

.badge-green {
    background: #ECFDF5;
    color: #10B981;
}

.badge-purple {
    background: #F5F3FF;
    color: #7C3AED;
}

.card-title {
    font-size: 21px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 10px;
    letter-spacing: -0.3px;
}

.card-desc {
    font-size: 14px;
    color: #64748B;
    line-height: 1.5;
    flex-grow: 1;
}

/* Action Buttons for Cards */
div.st-key-btn_report button {
    background-color: #3B82F6 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 18px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
div.st-key-btn_report button:hover {
    background-color: #2563EB !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px);
}

div.st-key-btn_symptoms button {
    background-color: #10B981 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 18px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
div.st-key-btn_symptoms button:hover {
    background-color: #059669 !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
    transform: translateY(-1px);
}

div.st-key-btn_medicine button {
    background-color: #8B5CF6 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 18px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
div.st-key-btn_medicine button:hover {
    background-color: #7C3AED !important;
    box-shadow: 0 4px 14px rgba(139, 92, 246, 0.35) !important;
    transform: translateY(-1px);
}

/* Back Button */
div.st-key-back_home button {
    background-color: white !important;
    color: #334155 !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 6px 14px !important;
    transition: all 0.2s ease !important;
}
div.st-key-back_home button:hover {
    background-color: #F1F5F9 !important;
    color: #0F172A !important;
    border-color: #94A3B8 !important;
}

/* Global Medical Disclaimer */
.global-disclaimer {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-radius: 12px;
    padding: 14px 18px;
    margin-top: 40px;
    font-size: 13px;
    color: #92400E;
    line-height: 1.5;
}
.global-disclaimer b {
    color: #78350F;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon-box">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.78-.77-.78a5.4 5.4 0 0 0-7.65 7.65l.77.78L12 20.66l7.65-7.65.77-.78a5.4 5.4 0 0 0 0-7.65z"></path>
                <path d="M12 12.5l1.5-2 1.5 4 1.5-3 1.5 1h2"></path>
            </svg>
        </div>
        <div class="brand-text">
            <div class="brand-title">Healthcare</div>
            <div class="brand-subtitle">Virtual Assistant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    menu_options = [
        "Home",
        "Report Explainer",
        "Symptoms Checker",
        "Medicine Information"
    ]

    menu_icons = {
        "Home": "🏠",
        "Report Explainer": "📄",
        "Symptoms Checker": "🩺",
        "Medicine Information": "💊"
    }

    display_options = [f"{menu_icons[k]}  {k}" for k in menu_options]

    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = "Home"

    # Find current index
    current_key = st.session_state["nav_selection"]
    current_index = menu_options.index(current_key) if current_key in menu_options else 0

    selected_display = st.radio(
        "Navigation",
        display_options,
        index=current_index,
        label_visibility="collapsed"
    )

    # Extract clean key
    selected_clean_key = selected_display.split("  ")[-1].strip()
    if selected_clean_key != st.session_state["nav_selection"]:
        st.session_state["nav_selection"] = selected_clean_key
        st.rerun()

    # Sidebar Footer Note
    st.markdown("""
    <div style="margin-top: 50px; padding: 14px; background: rgba(255,255,255,0.04); border-radius: 10px; font-size: 11px; color: #64748B; line-height: 1.4;">
        🔒 <b>Safe & Private:</b> Your medical inquiries and uploaded lab records are processed securely and never stored.
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# TOP GREETING HEADER
# ------------------------------------------
c_space, c_greet = st.columns([4, 1.2])
with c_greet:
    st.markdown("""
    <div class="top-greeting">
        <div class="greeting-hello">Hello!</div>
        <div class="greeting-sub">Your health matters <span style="color: #94A3B8;">🤍</span></div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 1. HOME DASHBOARD
# ==========================================
if st.session_state["nav_selection"] == "Home":
    # Hero Welcome Card (Exact match to design mockup)
    st.markdown("""
<div class="hero-card">
    <div style="flex: 1; min-width: 320px;">
        <div class="hero-welcome-badge">Welcome to</div>
        <div class="hero-title">Healthcare Virtual Assistant</div>
        <p class="hero-subtitle">Get quick and reliable information about your health.<br>Choose a module below to get started.</p>
    </div>
    <div style="display: flex; justify-content: flex-end; align-items: center; min-width: 220px;">
        <svg width="220" height="155" viewBox="0 0 220 155" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M40 80C25 35 75 15 130 25C180 35 210 70 195 110C180 145 130 152 85 145C45 135 55 110 40 80Z" fill="#D7E8FD"/>
            <path d="M105 120C105 120 60 90 60 62C60 46 72 34 88 34C98 34 105 40 105 40C105 40 112 34 122 34C138 34 150 46 150 62C150 90 105 120 105 120Z" fill="#2B60E6"/>
            <path d="M68 64L80 64L86 50L93 78L100 56L106 70L110 64L142 64" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M136 62C150 62 168 78 166 102C164 126 142 140 118 140C94 140 82 126 84 114" stroke="#1E293B" stroke-width="4" stroke-linecap="round"/>
            <path d="M160 106C172 106 178 114 178 126" stroke="#1E293B" stroke-width="3.5" stroke-linecap="round"/>
            <circle cx="84" cy="112" r="7" fill="#64748B" stroke="#1E293B" stroke-width="2.5"/>
            <circle cx="84" cy="112" r="3" fill="#E2E8F0"/>
            <circle cx="178" cy="126" r="4" fill="#0F172A"/>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

    # 3 Feature Cards Side-by-Side Grid
    col1, col2, col3 = st.columns(3)

    def navigate_to(page_name):
        st.session_state["nav_selection"] = page_name

    # Card 1: Report Explainer
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-badge badge-blue">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 8 9"></polyline>
                </svg>
            </div>
            <div class="card-title">Report Explainer</div>
            <div class="card-desc">Upload your medical report (image, PDF or text) and get a simple, easy-to-understand explanation of the results.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started →", key="btn_report", use_container_width=True):
            navigate_to("Report Explainer")
            st.rerun()

    # Card 2: Symptoms Checker
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-badge badge-green">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"></path>
                    <path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"></path>
                    <circle cx="20" cy="10" r="2"></circle>
                </svg>
            </div>
            <div class="card-title">Symptoms Checker</div>
            <div class="card-desc">Enter your symptoms and get possible conditions, precautions, and next steps based on the information you provide.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started →", key="btn_symptoms", use_container_width=True):
            navigate_to("Symptoms Checker")
            st.rerun()

    # Card 3: Medicine Information
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="icon-badge badge-purple">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"></path>
                    <path d="m8.5 8.5 7 7"></path>
                </svg>
            </div>
            <div class="card-title">Medicine Information</div>
            <div class="card-desc">Search for any medicine and get details like uses, dosage, side effects, and important precautions.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started →", key="btn_medicine", use_container_width=True):
            navigate_to("Medicine Information")
            st.rerun()

# ==========================================
# 2. REPORT EXPLAINER MODULE
# ==========================================
elif st.session_state["nav_selection"] == "Report Explainer":
    c_btn, c_title = st.columns([1.2, 5.8])
    with c_btn:
        if st.button("← Back to Home", key="back_home_report", use_container_width=True):
            st.session_state["nav_selection"] = "Home"
            st.rerun()

    report_engine = get_report_engine()

    st.markdown("""
    <div style="margin-top: 10px; margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0 0 6px 0;">📄 Medical Report Explainer & Lab Triage</h2>
        <p style="color: #64748B; font-size: 15px; margin: 0;">Upload your diagnostic lab test results (<b>PDF, JPG, PNG</b>) or paste your parameters directly. AI reads only your report values to produce an unbiased explanation.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Lab Report (PDF, JPG, PNG, JPEG)",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Upload a digital PDF from your diagnostic lab or a clear photo of your test paper."
    )

    with st.expander("📝 Or Type / Paste Lab Report Text Directly"):
        pasted_text = st.text_area(
            "Enter report parameters and numbers here:",
            placeholder="E.g., Hemoglobin: 10.2 g/dL, WBC: 12000, Fasting Blood Sugar: 140 mg/dL, Platelets: 180000...",
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

# ==========================================
# 3. SYMPTOMS CHECKER MODULE
# ==========================================
elif st.session_state["nav_selection"] == "Symptoms Checker":
    c_btn, c_title = st.columns([1.2, 5.8])
    with c_btn:
        if st.button("← Back to Home", key="back_home_symptoms", use_container_width=True):
            st.session_state["nav_selection"] = "Home"
            st.rerun()

    symptom_engine = get_symptom_engine()

    col_head, col_act = st.columns([3.5, 1])
    with col_head:
        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 14px;">
            <h2 style="font-weight: 800; color: #0F172A; margin: 0 0 6px 0;">🩺 Symptoms Checker & Clinical Triage</h2>
            <p style="color: #64748B; font-size: 15px; margin: 0;">Have a direct consultation with your virtual health assistant. Describe what you're feeling to receive structured guidance.</p>
        </div>
        """, unsafe_allow_html=True)
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
            "Your symptoms may indicate an emergency requiring immediate in-person medical attention:\n"
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

# ==========================================
# 4. MEDICINE INFORMATION MODULE
# ==========================================
elif st.session_state["nav_selection"] == "Medicine Information":
    c_btn, c_title = st.columns([1.2, 5.8])
    with c_btn:
        if st.button("← Back to Home", key="back_home_med", use_container_width=True):
            st.session_state["nav_selection"] = "Home"
            st.rerun()

    medicine_engine = get_medicine_engine()

    st.markdown("""
    <div style="margin-top: 10px; margin-bottom: 16px;">
        <h2 style="font-weight: 800; color: #0F172A; margin: 0 0 6px 0;">💊 Medicine Information & Safety Lookup</h2>
        <p style="color: #64748B; font-size: 15px; margin: 0;">Search any medicine brand or generic name worldwide — learn about uses, standard dosage guidelines, side effects, and precautions in simple steps.</p>
    </div>
    """, unsafe_allow_html=True)

    if "med_query" not in st.session_state:
        st.session_state["med_query"] = ""
    if "searched_med" not in st.session_state:
        st.session_state["searched_med"] = ""
    if "current_medicine_result" not in st.session_state:
        st.session_state["current_medicine_result"] = ""

    st.caption("Quick Medication Lookups:")
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

    col_input, col_btn = st.columns([4.2, 1])
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

# ==========================================
# 5. GLOBAL MEDICAL DISCLAIMER FOOTER
# ==========================================
st.markdown("""
<div class="global-disclaimer">
    ⚠️ <b>MEDICAL DISCLAIMER:</b> This Healthcare Virtual Assistant is designed strictly for informational and educational triage assistance. 
    It is <b>NOT</b> a substitute for professional medical diagnosis, clinical evaluation, or treatment. 
    Always seek the direct guidance of a licensed physician or healthcare specialist for any medical condition. 
    In case of an emergency, call <b>108</b> (India) or <b>911</b> (US) immediately.
</div>
""", unsafe_allow_html=True)
