import os
import sys
import streamlit as st

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from views.user import user_page
from views.admin import admin_page
from views.feedback import feedback_page
from views.about import about_page
from views.home import home_page

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ================= GLOBAL CSS =================
st.markdown(
    """
    <style>

    /* ===== MAIN BACKGROUND ===== */
    .stApp {
        background-color: #0f172a;
    }

    /* ===== TOP HEADER FIX (IMPORTANT) ===== */
    header[data-testid="stHeader"] {
        background-color: #0f172a;
        border-bottom: 1px solid #1f2937;
    }

    /* ===== PAGE WIDTH ===== */
    .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }

    /* ===== HEADINGS ===== */
    h1 {
        color: #f8fafc;
        font-weight: 800;
    }

    h2, h3 {
        color: #e5e7eb;
        font-weight: 700;
    }

    /* ===== TEXT ===== */
    p, li, span {
        color: #cbd5f5;
        font-size: 16px;
    }

    /* ===== CARDS ===== */
    .card {
        background-color: #111827;
        padding: 1.6rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        border: 1px solid #1f2937;

        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .card-auto {
        background-color: #111827;
        padding: 1.6rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        border: 1px solid #1f2937;
        height: auto;
    }

    /* ===== CTA ===== */
    .cta {
        background: linear-gradient(135deg, #2563eb, #1e40af);
        color: #ffffff;
        padding: 1.6rem;
        border-radius: 18px;
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.5);
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    /* ===== DIVIDER ===== */
    hr {
        border-color: rgba(255,255,255,0.1);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================

def main():
    st.sidebar.title("AI Resume Analyzer")
    st.sidebar.caption("Smart resume analysis & insights")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "👤 User",
            "💬 Feedback",
            "ℹ️ About",
            "🛠️ Admin"
        ]
    )

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
