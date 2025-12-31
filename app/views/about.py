import streamlit as st
from backend.database.contact import save_contact_request


def about_page():
    # ---------- HERO ----------
    st.markdown(
        "<div style='text-align:center; padding:30px 0; max-width:700px; margin:auto;'>"
        "<h1>AI Resume Analyzer</h1>"
        "<p style='font-size:16px; opacity:0.8;'>"
        "Smart, transparent resume insights for students and job seekers"
        "</p>"
        "</div>",
        unsafe_allow_html=True
    )

    # ---------- ABOUT CARD ----------
    st.markdown(
        "<div style='padding:24px; border-radius:12px; border:1px solid #e0e0e0; "
        "max-width:900px; margin:auto;'>"
        "<h3>📄 About the Project</h3>"
        "<p>"
        "This project helps users analyze resumes, identify skill gaps, "
        "understand experience levels, and evaluate how well their profile "
        "aligns with specific job roles."
        "</p>"
        "<h4 style='margin-top:20px;'>🎯 Why this project?</h4>"
        "<ul>"
        "<li>Clear, explainable resume insights</li>"
        "<li>Useful for students and early professionals</li>"
        "</ul>"
        "<h4 style='margin-top:20px;'>🛠 Tech Stack</h4>"
        "<ul>"
        "<li>Python</li>"
        "<li>Streamlit</li>"
        "<li>MongoDB</li>"
        "<li>NLP (Embeddings & Cosine Similarity)</li>"
        "</ul>"
        "</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # ---------- CONTACT HEADER ----------
    st.markdown(
        "<div style='text-align:center;'>"
        "<h3>🤝 Contact / Collaborate</h3>"
        "<p style='opacity:0.8;'>"
        "Interested in collaborating, contributing, or have a question?"
        "</p>"
        "</div>",
        unsafe_allow_html=True
    )

    # ---------- CONTACT FORM ----------
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email *")
        message = st.text_area("Message *", height=120)

        submitted = st.form_submit_button("📩 Send Message")

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------- LOGIC (UNCHANGED) ----------
        if submitted:
            if not email.strip() or not message.strip():
                st.error("Email and message are required.")
            else:
                save_contact_request(
                    name=name,
                    email=email,
                    message=message
                )
                st.success("Your message has been sent successfully! 🙌")
