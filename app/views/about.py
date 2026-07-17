import streamlit as st
from backend.database.contact import save_contact_request


def about_page():

    # ---------- HERO ----------
    st.markdown(
        """
        <style>
        .pg-badge b { color: #a5b4fc !important; -webkit-text-fill-color: #a5b4fc !important; }
        </style>
        <div style='text-align:center; padding: 2.5rem 1rem 1.5rem;'>
            <div class='pg-badge' style='display:inline-block; background: rgba(99,102,241,0.15);
                        border: 1px solid rgba(99,102,241,0.4);
                        padding:5px 16px; border-radius:999px; margin-bottom:1rem;'>
                <b style='font-size:11px; font-weight:700;
                          text-transform:uppercase; letter-spacing:1px;'>Open Source Project</b>
            </div>
            <h1 style='font-size:2.6rem; margin:0.4rem 0;'>AI Resume Analyzer</h1>
            <p style='font-size:16px; color:#64748b; max-width:520px; margin:0.8rem auto 0; line-height:1.7;'>
                Smart, transparent resume insights for students and job seekers —
                built with explainability and real-world usability in mind.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------- ABOUT CARD ----------
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            <div class="card-auto">
                <h3 style='margin-top:0;'>📄 About the Project</h3>
                <p>
                    This project helps users analyze resumes, identify skill gaps,
                    understand experience levels, and evaluate how well their profile
                    aligns with specific job roles using semantic AI techniques.
                </p>
                <h3 style='margin-top:1.2rem;'>🎯 Why this project?</h3>
                <ul style='padding-left:1.2rem; margin:0;'>
                    <li>Clear, explainable resume insights — no black-box decisions</li>
                    <li>Useful for students and early-career professionals</li>
                    <li>AI-powered skill extraction using Groq (Llama 3) — context-aware, not just keywords</li>
                    <li>Production-ready architecture with MongoDB persistence</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card-auto" style="height:100%;">
                <h3 style='margin-top:0;'>🛠 Tech Stack</h3>
                <div style='margin-top:0.6rem;'>
                    <span class='tech-badge'>Python</span>
                    <span class='tech-badge'>Streamlit</span>
                    <span class='tech-badge'>MongoDB</span>
                    <span class='tech-badge'>Groq API</span>
                    <span class='tech-badge'>Llama 3</span>
                    <span class='tech-badge'>SentenceTransformers</span>
                    <span class='tech-badge'>scikit-learn</span>
                    <span class='tech-badge'>pdfminer</span>
                    <span class='tech-badge'>Plotly</span>
                    <span class='tech-badge'>KMeans</span>
                    <span class='tech-badge'>bcrypt</span>
                    <span class='tech-badge'>pymongo</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ---------- CONTACT ----------
    st.markdown(
        """
        <div style='text-align:center; margin-bottom:1.5rem;'>
            <h2>🤝 Get in Touch</h2>
            <p style='color:#64748b;'>Interested in collaborating, contributing, or have a question?</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("contact_form"):
            name = st.text_input("Name", placeholder="Your name...")
            email = st.text_input("Email *", placeholder="your@email.com")
            message = st.text_area("Message *", height=130,
                                   placeholder="Tell us what's on your mind...")

            submitted = st.form_submit_button("📩 Send Message", width="stretch")

            if submitted:
                if not email.strip() or not message.strip():
                    st.error("❌ Email and message are required.")
                else:
                    save_contact_request(
                        name=name,
                        email=email,
                        message=message
                    )
                    st.success("🙌 Your message has been sent successfully!")

    st.divider()

    # ---------- AUTHOR ----------
    st.markdown(
        """
        <div style='text-align:center; padding:1.5rem;'>
            <div class="card-auto" style='max-width:400px; margin:0 auto; text-align:center;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>👨‍💻</div>
                <h3 style='margin:0 0 0.3rem;'>Developed by Chidvilas</h3>
                <p style='color:#64748b; font-size:13px; margin:0;'>
                    📧 <a href='mailto:palarpachidvilas2419@gmail.com'
                          style='color:#a5b4fc; text-decoration:none;'>
                        palarpachidvilas2419@gmail.com
                    </a>
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )



