import streamlit as st
from backend.database.auth import verify_user, register_user


def login_page():

    st.markdown("""
    <style>

    /* Hide streamlit default padding */
    .block-container { padding-top: 3rem !important; }

    /* Center card wrapper */
    .login-outer {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding-top: 2rem;
    }

    /* The main card */
    .login-card {
        background: rgba(10, 16, 30, 0.95);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 24px;
        padding: 2.8rem 2.4rem 2.2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6), 0 0 60px rgba(99,102,241,0.06);
        backdrop-filter: blur(16px);
        width: 100%;
    }

    /* Branding inside card */
    .lc-brand {
        text-align: center;
        margin-bottom: 2rem;
    }
    .lc-icon {
        font-size: 2.6rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    .lc-title {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(120deg, #818cf8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.25rem 0;
    }
    .lc-sub {
        color: #475569;
        font-size: 0.82rem;
        margin: 0;
    }

    .lc-divider {
        border: none;
        border-top: 1px solid rgba(99,102,241,0.12);
        margin: 1.4rem 0 1.6rem;
    }

    /* Style the Streamlit tabs to look integrated */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(99,102,241,0.07) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid rgba(99,102,241,0.12) !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #64748b !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.35) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # Centered narrow column
    _, center, _ = st.columns([1, 1.6, 1])

    with center:
        # Card header (branding)
        st.markdown("""
        <div class="login-card">
            <div class="lc-brand">
                <span class="lc-icon">📄</span>
                <p class="lc-title">AI Resume Analyzer</p>
                <p class="lc-sub">Your smart career companion</p>
            </div>
            <hr class="lc-divider">
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑  Sign In", "✨  Register"])

        # ─── LOGIN TAB ───────────────────────────────────────────
        with tab1:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            if st.button("Sign In  →", type="primary", use_container_width=True, key="login_btn"):
                if not username or not password:
                    st.warning("⚠️ Please fill in all fields")
                else:
                    user = verify_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user["username"]
                        st.session_state.role = user["role"]
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")

        # ─── REGISTER TAB ────────────────────────────────────────
        with tab2:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            new_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
            new_password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            if st.button("Create Account  →", type="primary", use_container_width=True, key="reg_btn"):
                if not new_username or not new_password or not confirm_password:
                    st.warning("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 6:
                    st.warning("⚠️ Password must be at least 6 characters")
                else:
                    result = register_user(new_username, new_password, "user")
                    if result:
                        # Auto-login after successful registration
                        user = verify_user(new_username, new_password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.username = user["username"]
                            st.session_state.role = user["role"]
                            st.success("✅ Account created! Logging you in...")
                            st.rerun()
                    else:
                        st.error("❌ Username already taken. Try another.")
