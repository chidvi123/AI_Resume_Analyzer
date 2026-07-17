import streamlit as st

def home_page():

    # ---------- HERO ----------
    st.markdown(
        """
        <style>
        .pg-badge b { color: #a5b4fc !important; -webkit-text-fill-color: #a5b4fc !important; }
        </style>
        <div style='text-align:center; padding: 3rem 1rem 2rem;'>
            <div class='pg-badge' style='display:inline-block; background: rgba(99,102,241,0.15);
                        border: 1px solid rgba(99,102,241,0.4);
                        padding:6px 18px; border-radius:999px; margin-bottom:1.2rem;'>
                <b style='font-size:12px; font-weight:700;
                          text-transform:uppercase; letter-spacing:1px;'>✨ AI-Powered Resume Intelligence</b>
            </div>
            <h1 style='font-size:3.2rem; font-weight:900; line-height:1.15; margin:0.5rem 0;
                       background: linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 55%, #8b5cf6 100%);
                       -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;'>
                Analyze Your Resume.<br>Land Your Dream Job.
            </h1>
            <p style='font-size:17px; color:#94a3b8; max-width:560px; margin:1rem auto 0; line-height:1.7;'>
                Upload your resume, identify skill gaps, and get a semantic job match score — all in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------- STATS ----------
    st.markdown(
        """
        <div class="stat-row">
            <div class="stat-item">
                <div class="stat-number">10+</div>
                <div class="stat-label">Job Roles</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">AI</div>
                <div class="stat-label">Semantic Matching</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">⚡</div>
                <div class="stat-label">Instant Analysis</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">100%</div>
                <div class="stat-label">Explainable</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------- FEATURE CARDS ----------
    st.markdown("<p class='section-label' style='text-align:center;'>What you get</p>", unsafe_allow_html=True)
    st.subheader("Why use AI Resume Analyzer?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
                <div>
                    <div style='font-size:2rem; margin-bottom:0.6rem;'>📄</div>
                    <h3>Resume Analysis</h3>
                    <p>Automatically extracts skills, experience level, and key sections from your resume with dictionary-based precision.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <div>
                    <div style='font-size:2rem; margin-bottom:0.6rem;'>🎯</div>
                    <h3>Skill Gap Detection</h3>
                    <p>Compare your skills with your target job role and see exactly what you need to learn next.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
                <div>
                    <div style='font-size:2rem; margin-bottom:0.6rem;'>📈</div>
                    <h3>Job Match Score</h3>
                    <p>Get a semantic similarity percentage showing how well your profile aligns with your desired role.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div class="card">
                <div>
                    <div style='font-size:2rem; margin-bottom:0.6rem;'>📚</div>
                    <h3>Course Recommendations</h3>
                    <p>Get curated course and certification recommendations tailored to your target role and skill gaps.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            """
            <div class="card">
                <div>
                    <div style='font-size:2rem; margin-bottom:0.6rem;'>🔍</div>
                    <h3>Explainable Scoring</h3>
                    <p>Every score comes with a transparent breakdown — no black-box decisions, just clear reasoning.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col6:
        st.markdown(
            """
            <div class="card">
                <div>
                    <div style='font-size:2rem; margin-bottom:0.6rem;'>🧠</div>
                    <h3>Admin Intelligence</h3>
                    <p>Admins get clustering, similarity search, and trend analytics powered by persisted embeddings.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ---------- HOW IT WORKS ----------
    st.subheader("How it works")
    st.caption("A simple 5-step process to analyze and improve your resume")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card-auto">
            <div class="step">
                <div class="step-num">1</div>
                <div class="step-content">
                    <strong>Upload your resume</strong>
                    <p>Drop your PDF resume — we extract text, name, email, and all key sections automatically.</p>
                </div>
            </div>
            <div class="step">
                <div class="step-num">2</div>
                <div class="step-content">
                    <strong>Select your target role</strong>
                    <p>Choose from 10 job roles — Data Scientist, Backend Developer, DevOps, and more.</p>
                </div>
            </div>
            <div class="step">
                <div class="step-num">3</div>
                <div class="step-content">
                    <strong>Get instant insights</strong>
                    <p>View your resume score, skill gaps, and semantic job match percentage in real time.</p>
                </div>
            </div>
            <div class="step">
                <div class="step-num">4</div>
                <div class="step-content">
                    <strong>Learn what's missing</strong>
                    <p>Get curated course recommendations and interview prep videos to close skill gaps.</p>
                </div>
            </div>
            <div class="step">
                <div class="step-num">5</div>
                <div class="step-content">
                    <strong>Share feedback or collaborate</strong>
                    <p>Rate your experience or reach out from the Feedback and About pages.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ---------- CTA ----------
    st.markdown(
        """
        <div class="cta">
            👉 Ready to begin? Head to the <b>User</b> page in the sidebar to upload your resume now.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)



