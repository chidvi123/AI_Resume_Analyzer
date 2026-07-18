import streamlit as st
import hashlib
from datetime import datetime
import requests
from streamlit_lottie import st_lottie
from backend.utils.helpers import save_uploaded_file
from backend.parser.pdf_reader import extract_text_from_pdf
from backend.parser.resume_parser import parse_resume
from backend.analysis.experience_level import detect_experience_level
from backend.analysis.resume_score import calculate_resume_score
from backend.analysis.skill_gap import analyze_skill_gap
from backend.utils.constants import ROLE_SKILLS
from backend.utils.normalizer import normalize_skills
from backend.utils.sematic_text_builder import build_semantic_resume_text
from backend.utils.job_roles import JOB_ROLE_DESCRIPTIONS
from backend.nlp.embeddings import get_embedding
from backend.nlp.similarity import cosine_similarity

from backend.recommender.course_recommender import (
    get_recommended_courses,
    resume_videos,
    interview_videos
    )
from backend.database.analytics import save_analytics_record
from backend.database.user_data import save_resume, get_resume_by_hash

@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def user_page():

    # ===================== HEADER =====================
    st.markdown(
        """
        <style>
        .pg-badge b { color: #a5b4fc !important; -webkit-text-fill-color: #a5b4fc !important; }
        </style>
        <div style='margin-bottom:0.8rem;'>
            <div class='pg-badge' style='display:inline-block; background:rgba(99,102,241,0.15);
                        border:1px solid rgba(99,102,241,0.4);
                        padding:5px 14px; border-radius:999px;'>
                <b style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px;'
                >Resume Analysis</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("AI Resume Analyzer")
    st.caption("Upload your resume and get clear, actionable insights in seconds")

    st.divider()

    # ===================== UPLOAD =====================
    uploaded_file = st.file_uploader("📄 Upload your resume (PDF only)", type=["pdf"])

    if uploaded_file is None:
        st.info("Please upload a PDF resume to continue.")
        st.stop()

    file_path = save_uploaded_file(uploaded_file)

    # ===================== TEXT EXTRACTION =====================
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<h4 style='text-align: center; color: #cbd5f5;'>🤖 AI is reading your resume...</h4>", unsafe_allow_html=True)
        lottie_json = load_lottieurl("https://lottie.host/4a5b06bd-bc27-4de0-8e6f-75895781a711/c9kI6N0j91.json")
        if lottie_json:
            st_lottie(lottie_json, height=200, key="loading")

    extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text or len(extracted_text.strip()) < 50:
        placeholder.empty()
        st.error("Could not extract enough text from this PDF.")
        st.stop()

    # Generate SHA-256 hash of raw text for deduplication check at the START
    resume_hash = hashlib.sha256(extracted_text.encode("utf-8")).hexdigest()
    existing = get_resume_by_hash(resume_hash)

    if existing:
        # Cache HIT: retrieve everything directly from MongoDB
        parsed_data = existing["parsed_data"]
        experience_level = existing["experience_level"]
        resume_score = existing["resume_score"]
        score_breakdown = existing.get("score_breakdown", {
            "Experience/Internship": 0, "Skills": 0, "Projects": 0,
            "Education": 0, "Summary/Objective": 0, "Certification": 0
        })
        semantic_text = existing.get("semantic_text", "")
        resume_embedding = existing["embedding"]
        st.toast("Loaded cached analysis from MongoDB! 💾", icon="💾")
    else:
        # Cache MISS: run full parsing and NLP pipeline
        parsed_data = parse_resume(extracted_text)
        experience_level = detect_experience_level(extracted_text)
        score_data = calculate_resume_score(extracted_text)
        resume_score = score_data["score"]
        score_breakdown = score_data["breakdown"]
        semantic_text = ""
        resume_embedding = None

    placeholder.empty()
    st.toast("Resume parsed successfully!", icon="✅")

    # ===================== ROLE SELECTION =====================
    st.subheader("🎯 Target Job Role")

    target_role = st.selectbox(
        "Select the role you are aiming for",
        list(JOB_ROLE_DESCRIPTIONS.keys())
    )

    confirm = st.button("Analyze for this role", type="primary")

    if not confirm:
        st.stop()

    st.divider()

    # ===================== TABS LAYOUT =====================
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary & Score", "🧠 Skill Gap", "🎯 Job Match", "📚 Resources"])

    with tab1:
        st.subheader("Resume Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"""
                <div class="metric-highlight">
                    <div class="mh-label">Experience Level</div>
                    <div class="mh-value">{experience_level}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            score_color = "#10b981" if resume_score >= 70 else "#f59e0b" if resume_score >= 45 else "#ef4444"
            st.markdown(
                f"""
                <div class="metric-highlight">
                    <div class="mh-label">Resume Score</div>
                    <div class="mh-value" style="background:linear-gradient(135deg,{score_color},{score_color}cc);
                         -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
                        {resume_score} <span style="font-size:1.1rem; font-weight:500;">/100</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("📊 Resume Score Breakdown"):
            total_possible = sum(v for v in score_breakdown.values() if v > 0) or 1
            for section, points in score_breakdown.items():
                max_pts = {"Experience/Internship": 25, "Skills": 20, "Projects": 20,
                           "Education": 15, "Summary/Objective": 10, "Certification": 10}.get(section, 10)
                pct = int((points / max_pts) * 100) if max_pts else 0
                bar_color = "#10b981" if points == max_pts else "#f59e0b" if points > 0 else "#ef4444"
                st.markdown(
                    f"""
                    <div class="score-row">
                        <div class="score-row-label">
                            <span>{section}</span>
                            <span style="color:{'#10b981' if points == max_pts else '#f59e0b' if points > 0 else '#ef4444'}">
                                {points} / {max_pts} pts
                            </span>
                        </div>
                        <div class="score-track">
                            <div class="score-fill" style="width:{pct}%; background:linear-gradient(90deg,{bar_color},{bar_color}cc);"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with tab2:
        resume_skills = normalize_skills(parsed_data.get("skills", []))
        required_skills = ROLE_SKILLS.get(target_role, [])

        skill_gap = analyze_skill_gap(resume_skills, required_skills)
        present_skills = skill_gap["present_skills"]
        missing_skills = skill_gap["missing_skills"]

        st.subheader("Skill Gap Analysis")

        total = len(required_skills)
        matched = len(present_skills)
        pct = int((matched / total) * 100) if total else 0

        st.markdown(
            f"""
            <div class="card-auto" style="margin-bottom:1.2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-size:13px; color:var(--text-secondary); font-weight:600;">
                        Skills matched: <span style="color:#34d399;">{matched}</span> / {total}
                    </span>
                    <span style="font-size:1.2rem; font-weight:800; color:#34d399;">{pct}%</span>
                </div>
                <div class="score-track">
                    <div class="score-fill" style="width:{pct}%; background:linear-gradient(90deg,#10b981,#34d399);"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("<p class='section-label'>✅ Skills You Have</p>", unsafe_allow_html=True)
            if present_skills:
                st.markdown(
                    " ".join(f"<span class='chip-green'>{s}</span>" for s in present_skills),
                    unsafe_allow_html=True
                )
            else:
                st.info("No matching skills found.")

        with col_b:
            st.markdown("<p class='section-label'>🚀 Skills to Learn</p>", unsafe_allow_html=True)
            if missing_skills:
                st.markdown(
                    " ".join(f"<span class='chip-red'>{s}</span>" for s in missing_skills),
                    unsafe_allow_html=True
                )
            else:
                st.toast("You already meet the skill requirements 🎉", icon="🎉")
                st.success("You meet all skill requirements for this role! 🎉")

    with tab3:

        # ===================== JOB MATCH =====================
        if not semantic_text or resume_embedding is None:
            semantic_text = build_semantic_resume_text(
                raw_text=extracted_text,
                skills=resume_skills,
                experience_level=experience_level
            )
            # Retrieve array, convert to list later for DB storage
            resume_embedding_val = get_embedding(semantic_text)
            resume_embedding = resume_embedding_val.tolist() if hasattr(resume_embedding_val, "tolist") else resume_embedding_val

        job_embedding = get_embedding(JOB_ROLE_DESCRIPTIONS[target_role])

        match_score = cosine_similarity(resume_embedding, job_embedding)
        match_percentage = int(round(match_score * 100, 0))

        match_color = "#10b981" if match_percentage >= 65 else "#f59e0b" if match_percentage >= 40 else "#ef4444"
        match_label = "Strong Match" if match_percentage >= 65 else "Moderate Match" if match_percentage >= 40 else "Needs Work"

        st.subheader("Job Match Score")
        st.markdown(
            f"""
            <div class="card-auto" style="text-align:center; padding: 2.5rem;">
                <div style="font-size:4rem; font-weight:900;
                            background:linear-gradient(135deg,{match_color},{match_color}99);
                            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                            background-clip:text; line-height:1;">
                    {match_percentage}%
                </div>
                <div style="margin:0.5rem 0 1.2rem; font-size:14px; color:{match_color}; font-weight:600;">
                    {match_label}
                </div>
                <div class="score-track" style="max-width:400px; margin:0 auto;">
                    <div class="score-fill"
                         style="width:{match_percentage}%; background:linear-gradient(90deg,{match_color},{match_color}cc);"></div>
                </div>
                <div style="margin-top:1rem; font-size:13px; color:var(--text-muted);">
                    Semantic similarity to <strong style="color:var(--text-secondary);">{target_role.replace('_',' ').title()}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab4:
        st.subheader("Learning Resources")
        # ===================== COURSES =====================
        with st.expander("📚 Recommended Courses & Certifications"):
            courses = get_recommended_courses(target_role)
            if courses:
                for title, link in courses[:5]:
                    st.write(f"- [{title}]({link})")
            else:
                st.info("No recommendations available for this role yet.")

        # ===================== VIDEOS =====================
        with st.expander("📄 Resume Building & Improvement Videos"):
            st.caption("Improve resume structure, wording, and ATS optimization")
            cols = st.columns(5)
            for i, video_url in enumerate(resume_videos):
                with cols[i % 5]:
                    st.video(video_url)

        with st.expander("💼 Interview Preparation Videos"):
            st.caption("Common interview questions, behavioral tips, and technical prep")
            cols = st.columns(5)
            for i, video_url in enumerate(interview_videos):
                with cols[i % 5]:
                    st.video(video_url)

    # ===================== SAVE ANALYTICS =====================
    if not existing:
        resume_record = {
            "resume_hash": resume_hash,
            "semantic_text": semantic_text,
            "parsed_data": parsed_data,
            "experience_level": experience_level,
            "resume_score": resume_score,
            "score_breakdown": score_breakdown,
            "embedding": resume_embedding,
        }
        save_resume(resume_record)
        existing = get_resume_by_hash(resume_hash)

    save_analytics_record({
        "username": st.session_state.username,
        "resume_id": existing["_id"],
        "timestamp": datetime.now(),
        "experience_level": experience_level,
        "resume_score": resume_score,
        "target_role": target_role,
        "job_match_score": match_score,
        "skills_present": present_skills,
        "skills_missing": missing_skills,
        "skills_present_count": len(present_skills),
        "skills_missing_count": len(missing_skills)
    })

    '''# ===================== TRANSPARENCY =====================
    with st.expander("🔍 View extracted resume text"):
        st.write(extracted_text)'''
