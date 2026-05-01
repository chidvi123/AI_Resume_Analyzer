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
    st.title("AI Resume Analyzer")
    st.caption("Upload your resume and get clear, actionable insights")

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

    parsed_data = parse_resume(extracted_text)
    experience_level = detect_experience_level(extracted_text)
    score_data = calculate_resume_score(extracted_text)
    resume_score = score_data["score"]
    score_breakdown = score_data["breakdown"]

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
            st.metric("Experience Level", experience_level)

        with col2:
            st.metric("Resume Score", f"{resume_score} / 100")

        with st.expander("ℹ️ Resume Score Breakdown"):
            for section, points in score_breakdown.items():
                st.write(f"- {section}: {points} points")

    with tab2:
        resume_skills = normalize_skills(parsed_data.get("skills", []))
        required_skills = ROLE_SKILLS.get(target_role, [])

        skill_gap = analyze_skill_gap(resume_skills, required_skills)
        present_skills = skill_gap["present_skills"]
        missing_skills = skill_gap["missing_skills"]

        st.subheader("Skill Gap Analysis")

        st.markdown("##### ✅ Your Current Skills")
        if present_skills:
            st.markdown(
                " ".join(
                    f"<span style='background:#2ecc71;color:white;padding:6px 10px;"
                    f"border-radius:12px;margin:4px;display:inline-block;font-size:14px;'>{s}</span>"
                    for s in present_skills
                ),
                unsafe_allow_html=True
            )
        else:
            st.info("No matching skills found.")

        st.markdown("##### 🚀 Recommended Skills to Learn")
        if missing_skills:
            st.markdown(
                " ".join(
                    f"<span style='background:#e74c3c;color:white;padding:6px 10px;"
                    f"border-radius:12px;margin:4px;display:inline-block;font-size:14px;'>{s}</span>"
                    for s in missing_skills
                ),
                unsafe_allow_html=True
            )
        else:
            st.toast("You already meet the skill requirements 🎉", icon="🎉")

    with tab3:

        # ===================== JOB MATCH =====================
        semantic_text = build_semantic_resume_text(
            raw_text=extracted_text,
            skills=resume_skills,
            experience_level=experience_level
        )

        resume_embedding = get_embedding(semantic_text)
        job_embedding = get_embedding(JOB_ROLE_DESCRIPTIONS[target_role])

        match_score = cosine_similarity(resume_embedding, job_embedding)
        match_percentage = int(round(match_score * 100, 0))

        st.subheader("📈 Job Match Score")
        st.metric("Match Percentage", f"{match_percentage}%")
        st.progress(match_percentage / 100.0, text=f"Similarity to {target_role}")

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
    resume_hash = hashlib.sha256(semantic_text.encode("utf-8")).hexdigest()

    resume_record = {
        "resume_hash": resume_hash,
        "semantic_text": semantic_text,
        "parsed_data": parsed_data,
        "experience_level": experience_level,
        "resume_score": resume_score,
        "skills_present": present_skills,
        "skills_missing": missing_skills,
        "embedding": resume_embedding.tolist(),
    }

    existing = get_resume_by_hash(resume_hash)
    if not existing:
        save_resume(resume_record)
        existing = get_resume_by_hash(resume_hash)

    save_analytics_record({
        "resume_id": existing["_id"],
        "timestamp": datetime.now(),
        "experience_level": experience_level,
        "resume_score": resume_score,
        "target_role": target_role,
        "job_match_score": match_score,
        "skills_present_count": len(present_skills),
        "skills_missing_count": len(missing_skills)
    })

    '''# ===================== TRANSPARENCY =====================
    with st.expander("🔍 View extracted resume text"):
        st.write(extracted_text)'''
