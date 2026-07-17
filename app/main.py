import os
import sys
import streamlit as st
import requests
from streamlit_lottie import st_lottie

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from views.user import user_page
from views.admin import admin_page
from views.feedback import feedback_page
from views.about import about_page
from views.home import home_page
from views.login import login_page

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ================= SESSION STATE =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# ================= GLOBAL CSS =================
st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ===== ROOT VARIABLES ===== */
    :root {
        --bg-base:       #070d1a;
        --bg-surface:    #0d1525;
        --bg-card:       rgba(13, 21, 37, 0.85);
        --bg-card-hover: rgba(20, 30, 55, 0.95);
        --accent-1:      #6366f1;
        --accent-2:      #8b5cf6;
        --accent-green:  #10b981;
        --accent-red:    #ef4444;
        --border:        rgba(99, 102, 241, 0.18);
        --border-hover:  rgba(99, 102, 241, 0.45);
        --text-primary:  #f1f5f9;
        --text-secondary:#94a3b8;
        --text-muted:    #475569;
        --glow-indigo:   0 0 24px rgba(99,102,241,0.35);
        --glow-green:    0 0 18px rgba(16,185,129,0.35);
        --glow-red:      0 0 18px rgba(239,68,68,0.35);
        --radius-sm:     10px;
        --radius-md:     16px;
        --radius-lg:     24px;
        --transition:    all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ===== GLOBAL ===== */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--bg-base) !important;
        color: var(--text-primary);
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--accent-1); border-radius: 8px; }

    /* ===== HEADER ===== */
    header[data-testid="stHeader"] {
        background: rgba(7, 13, 26, 0.92) !important;
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border);
    }

    /* ===== BLOCK CONTAINER ===== */
    .block-container {
        padding-top: 5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* ===== HEADINGS ===== */
    h1 {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 60%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
        line-height: 1.2 !important;
    }

    h2 {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    h3 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    p, li {
        color: var(--text-secondary);
        font-size: 15px;
        line-height: 1.65;
    }

    span, label {
        line-height: 1.65;
    }

    /* ===== BADGE TEXT — force b/strong to inherit from parent div's color ===== */
    .stMarkdown b,
    .stMarkdown strong {
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
    }

    /* Chip classes */
    .chip-green  { color: #34d399 !important; -webkit-text-fill-color: #34d399 !important; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; display: inline-block; margin: 3px; }
    .chip-red    { color: #f87171 !important; -webkit-text-fill-color: #f87171 !important; background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3); padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; display: inline-block; margin: 3px; }
    .tech-badge  { color: #a5b4fc !important; -webkit-text-fill-color: #a5b4fc !important; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.25); padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; display: inline-block; margin: 3px 4px; }
    .section-label { color: var(--text-muted) !important; -webkit-text-fill-color: var(--text-muted) !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; }

    /* ===== DIVIDER ===== */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--border), transparent) !important;
        margin: 2rem 0 !important;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-secondary) !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        background: none !important;
    }

    /* ===== CARDS ===== */
    .card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 1.8rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        transition: var(--transition);
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
        opacity: 0;
        transition: var(--transition);
    }

    .card:hover {
        border-color: var(--border-hover);
        box-shadow: var(--glow-indigo), 0 8px 32px rgba(0,0,0,0.5);
        transform: translateY(-4px);
    }

    .card:hover::before { opacity: 1; }

    .card h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }

    .card p {
        color: var(--text-secondary) !important;
    }

    .card-auto {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 1.8rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        height: auto;
    }

    /* ===== CTA ===== */
    .cta {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: #ffffff !important;
        padding: 1.8rem 2.4rem;
        border-radius: var(--radius-lg);
        text-align: center;
        font-size: 18px;
        font-weight: 700;
        box-shadow: 0 0 40px rgba(99,102,241,0.4), 0 10px 30px rgba(0,0,0,0.4);
        animation: pulse-glow 3s ease-in-out infinite;
    }

    .cta * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 40px rgba(99,102,241,0.35), 0 10px 30px rgba(0,0,0,0.4); }
        50%       { box-shadow: 0 0 65px rgba(139,92,246,0.6),  0 10px 40px rgba(0,0,0,0.5); }
    }

    /* ===== STAT ROW ===== */
    .stat-row {
        display: flex;
        justify-content: center;
        gap: 3rem;
        flex-wrap: wrap;
        padding: 1.6rem 2rem;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        margin: 1.5rem 0;
    }

    .stat-item { text-align: center; }

    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stat-label {
        font-size: 12px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }

    /* ===== STEP TIMELINE ===== */
    .step {
        display: flex;
        align-items: flex-start;
        gap: 1.2rem;
        padding: 1.1rem 0;
        border-bottom: 1px solid var(--border);
    }

    .step:last-child { border-bottom: none; }

    .step-num {
        min-width: 38px;
        height: 38px;
        background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 15px;
        color: white;
        box-shadow: var(--glow-indigo);
        flex-shrink: 0;
    }

    .step-content strong { color: var(--text-primary); font-size: 15px; display: block; margin-bottom: 3px; }
    .step-content p { color: var(--text-secondary); font-size: 13px; margin: 0; }

    /* ===== SKILL CHIPS ===== */
    .chip-green {
        display: inline-block;
        background: rgba(16,185,129,0.12);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.28);
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 500;
        margin: 4px;
        transition: var(--transition);
    }

    .chip-green:hover {
        background: rgba(16,185,129,0.22);
        box-shadow: var(--glow-green);
    }

    .chip-red {
        display: inline-block;
        background: rgba(239,68,68,0.10);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.22);
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 500;
        margin: 4px;
        transition: var(--transition);
    }

    .chip-red:hover {
        background: rgba(239,68,68,0.20);
        box-shadow: var(--glow-red);
    }

    /* ===== TECH BADGE ===== */
    .tech-badge {
        display: inline-block;
        background: rgba(99,102,241,0.10);
        color: #a5b4fc;
        border: 1px solid rgba(99,102,241,0.22);
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 500;
        margin: 5px;
        transition: var(--transition);
    }

    .tech-badge:hover {
        background: rgba(99,102,241,0.20);
        box-shadow: var(--glow-indigo);
    }

    /* ===== FEEDBACK CARD ===== */
    .feedback-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.4rem 1.6rem;
        margin-bottom: 14px;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .feedback-card::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, var(--accent-1), var(--accent-2));
    }

    .feedback-card:hover {
        border-color: var(--border-hover);
        box-shadow: var(--glow-indigo);
    }

    /* ===== SCORE BREAKDOWN ROW ===== */
    .score-row {
        margin: 8px 0;
    }

    .score-row-label {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 5px;
    }

    .score-track {
        height: 8px;
        background: rgba(255,255,255,0.06);
        border-radius: 999px;
        overflow: hidden;
    }

    .score-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
        box-shadow: 0 0 10px rgba(99,102,241,0.45);
    }

    /* ===== SECTION LABEL ===== */
    .section-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-muted);
        margin-bottom: 10px;
    }

    /* ===== METRIC HIGHLIGHT ===== */
    .metric-highlight {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.6rem;
        text-align: center;
        transition: var(--transition);
    }

    .metric-highlight:hover {
        border-color: var(--border-hover);
        box-shadow: var(--glow-indigo);
        transform: translateY(-3px);
    }

    .metric-highlight .mh-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-muted);
        margin-bottom: 8px;
    }

    .metric-highlight .mh-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f1f5f9, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }

    /* ===== STREAMLIT OVERRIDES ===== */

    .stButton > button {
        background: linear-gradient(135deg, var(--accent-1), var(--accent-2)) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.55rem 1.6rem !important;
        font-size: 14px !important;
        transition: var(--transition) !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.3) !important;
    }

    /* Streamlit wraps button text in various elements — nuke ALL of them */
    .stButton button *,
    .stButton button p,
    .stButton button div,
    .stButton button span,
    button[kind="primary"] *,
    button[kind="secondary"] * {
        color: white !important;
        -webkit-text-fill-color: white !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(99,102,241,0.5) !important;
        opacity: 0.95 !important;
    }

    .stTextInput input, .stTextArea textarea {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent-1) !important;
        box-shadow: var(--glow-indigo) !important;
    }

    .stSelectbox > div > div {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-surface) !important;
        border-radius: var(--radius-sm) !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition) !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-1), var(--accent-2)) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.4) !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--text-muted) !important;
    }

    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border-hover) !important;
        border-radius: var(--radius-md) !important;
        background: rgba(99,102,241,0.04) !important;
        transition: var(--transition) !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-1) !important;
        background: rgba(99,102,241,0.08) !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2)) !important;
        border-radius: 999px !important;
    }

    .stProgress > div {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 999px !important;
        height: 10px !important;
    }

    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem !important;
    }

    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
        font-size: 13px !important;
    }

    .stNumberInput input {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-sm) !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================

@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def main():
    # Gate: show login if not logged in
    if not st.session_state.logged_in:
        login_page()
        return

    st.sidebar.title("AI Resume Analyzer")
    st.sidebar.caption(f"👋 Welcome, {st.session_state.username}")
    st.sidebar.divider()

    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    lottie_json = load_lottieurl("https://lottie.host/4a5b06bd-bc27-4de0-8e6f-75895781a711/c9kI6N0j91.json")
    if lottie_json:
        with st.sidebar:
            st_lottie(lottie_json, height=120, key="sidebar_lottie")
            st.divider()

    # Role-based navigation
    if st.session_state.role == "admin":
        pages = ["🏠 Home", "👤 User", "💬 Feedback", "ℹ️ About", "🛠️ Admin"]
    else:
        pages = ["🏠 Home", "👤 User", "💬 Feedback", "ℹ️ About"]

    page = st.sidebar.radio("Navigation", pages)

    if page == "🏠 Home":
        home_page()
    elif page == "👤 User":
        user_page()
    elif page == "💬 Feedback":
        feedback_page()
    elif page == "ℹ️ About":
        about_page()
    elif page == "🛠️ Admin":
        admin_page()

if __name__ == "__main__":
    main()
