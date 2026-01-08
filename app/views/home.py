import streamlit as st

def home_page():

    # ---------- HERO ----------
    st.markdown(
        """
        <h1 style='text-align:center;'>🚀 AI Resume Analyzer</h1>
        <p style='text-align:center; font-size:18px; color:#4b5563;'>
            Analyze your resume, identify skill gaps, and improve your job match — instantly.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------- WHY USE ----------
    st.subheader("Why use AI Resume Analyzer?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h3>📄 Resume Analysis</h3>
                <p>
                Automatically extracts skills, experience level,
                and key sections from your resume.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>🎯 Skill Gap Detection</h3>
                <p>
                Compare your skills with your target job role
                and see exactly what you need to improve.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
                <h3>📈 Job Match Score</h3>
                <p>
                Get a clear percentage showing how well your resume
                matches your desired role.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ---------- HOW IT WORKS ----------
    st.subheader("How it works")
    st.caption("A simple 5-step process to analyze and improve your resume")

    with st.container():
        st.markdown(
            """
            <div class="card-auto">

            <b>1️⃣ Upload your resume</b><br>
            Upload your resume in PDF format.<br><br>

            <b>2️⃣ Select your target role</b><br>
            Choose the job role you are aiming for.<br><br>

            <b>3️⃣ Get instant insights</b><br>
            View skill gaps, resume score, and job match percentage.<br><br>

            <b>4️⃣ Share your feedback</b><br>
            Review your experience and help us improve from the Feedback page.<br><br>

            <b>5️⃣ Want to collaborate?</b><br>
            Learn more and reach out to us from the About page.

            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ---------- CTA ----------
    st.markdown(
        """
        <div class="cta">
            👉 Ready to begin? Use the sidebar to upload your resume and start analyzing now.
        </div>
        """,
        unsafe_allow_html=True
    )
