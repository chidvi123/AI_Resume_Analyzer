import streamlit as st
import hashlib
from datetime import datetime
from backend.utils.helpers import save_uploaded_file, show_pdf
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
from backend.recommender.course_recommender import get_recommended_courses
from backend.database.analytics import save_analytics_record
from backend.database.user_data import save_resume, get_resume_by_hash


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

    # ===================== PREVIEW =====================
    st.subheader("📄 Resume Preview")
    show_pdf(file_path)

    st.divider()

    # ===================== TEXT EXTRACTION =====================
    extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text or len(extracted_text.strip()) < 50:
        st.error("Could not extract enough text from this PDF.")
        st.stop()

    parsed_data = parse_resume(extracted_text)

    # ===================== EXPERIENCE & SCORE =====================
    experience_level = detect_experience_level(extracted_text)

    score_data = calculate_resume_score(extracted_text)
    resume_score = score_data["score"]
    score_breakdown = score_data["breakdown"]

    st.subheader("📊 Resume Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Experience Level", experience_level)

    with col2:
        st.metric("Resume Score", f"{resume_score} / 100")

    with st.expander("ℹ️ Resume Score Breakdown"):
        for section, points in score_breakdown.items():
            st.write(f"- {section}: {points} points")

    st.divider()

    # ===================== ROLE SELECTION =====================
    st.subheader("🎯 Target Job Role")

    target_role = st.selectbox(
        "Select the role you are aiming for",
        list(JOB_ROLE_DESCRIPTIONS.keys())
    )

    confirm = st.button("Analyze for this role")

    if not confirm:
        st.stop()

    # ===================== SKILL GAP =====================
    resume_skills = normalize_skills(parsed_data.get("skills", []))
    required_skills = ROLE_SKILLS.get(target_role, [])

    skill_gap = analyze_skill_gap(resume_skills, required_skills)

    present_skills = skill_gap["present_skills"]
    missing_skills = skill_gap["missing_skills"]

    st.divider()
    st.subheader("🧠 Skill Gap Analysis")

    st.markdown("### ✅ Your Current Skills")
    if present_skills:
        st.markdown(
            " ".join(
                f"<span style='background:#2ecc71;color:white;padding:6px 10px;"
                f"border-radius:12px;margin:4px;display:inline-block;'>{s}</span>"
                for s in present_skills
            ),
            unsafe_allow_html=True
        )
    else:
        st.info("No matching skills found.")

    st.markdown("### 🚀 Recommended Skills to Learn")
    if missing_skills:
        st.markdown(
            " ".join(
                f"<span style='background:#e74c3c;color:white;padding:6px 10px;"
                f"border-radius:12px;margin:4px;display:inline-block;'>{s}</span>"
                for s in missing_skills
            ),
            unsafe_allow_html=True
        )
    else:
        st.success("You already meet the skill requirements 🎉")

    st.divider()

    # ===================== JOB MATCH =====================
    semantic_text = build_semantic_resume_text(
        raw_text=extracted_text,
        skills=resume_skills,
        experience_level=experience_level
    )

    resume_embedding = get_embedding(semantic_text)
    job_embedding = get_embedding(JOB_ROLE_DESCRIPTIONS[target_role])

    match_score = cosine_similarity(resume_embedding, job_embedding)

    st.subheader("📈 Job Match Score")
    st.metric("Match Percentage", f"{round(match_score * 100, 1)}%")

    st.divider()

    # ===================== COURSES =====================
    with st.expander("📚 Recommended Courses & Certifications"):
        courses = get_recommended_courses(target_role)
        if courses:
            for title, link in courses:
                st.write(f"- [{title}]({link})")
        else:
            st.info("No recommendations available for this role yet.")

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

    # ===================== TRANSPARENCY =====================
    with st.expander("🔍 View extracted resume text"):
        st.write(extracted_text)
