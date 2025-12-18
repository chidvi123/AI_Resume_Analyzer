import streamlit as st
from datetime import datetime
from backend.utils.helpers import save_uploaded_file, show_pdf
from backend.parser.pdf_reader import extract_text_from_pdf
from backend.parser.resume_parser import parse_resume
from backend.analysis.experience_level import detect_experience_level
from backend.analysis.resume_score import calculate_resume_score
from backend.analysis.skill_gap import analyze_skill_gap
from backend.utils.constants import ROLE_SKILLS
from backend.nlp.embeddings import get_embedding
from backend.utils.job_roles import JOB_ROLE_DESCRIPTIONS
from backend.nlp.similarity import cosine_similarity
from backend.utils.text_cleaner import clean_resume_text
from backend.utils.normalizer import normalize_skills
from backend.utils.sematic_text_builder import build_semantic_resume_text

# ================================
# MODULE 1: USER RESUME ANALYSIS
# Status: Feature-complete
# ================================

def user_page():

    if "admin_analytics" not in st.session_state:
        st.session_state["admin_analytics"] = []

    if "analytics_saved" not in st.session_state:
        st.session_state["analytics_saved"] = False

    st.title("User Dashboard..")
    st.write("Please upload your resume in PDF Format to begin analysis.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file is None:
        st.info("Please upload a PDF resume to continue")
        st.stop()

    st.success("Resume uploaded successfully..")
    st.session_state["analytics_saved"] = False

    file_path = save_uploaded_file(uploaded_file)
    st.write("File saved at :", file_path)

    st.subheader("Preview")
    show_pdf(file_path)

    st.subheader("Extracted text from PDF")
    try:
        extracted_text = extract_text_from_pdf(file_path)
    except Exception:
        st.error("Unable to read PDF ,Please upload a valid resume file .")
        st.stop()

    if not extracted_text or len(extracted_text.strip()) < 50:
        st.error("Resume text could not be extracted properly. Please upload a clearer PDF")
        st.stop()

    with st.expander("Show extracted text"):
        st.write(extracted_text)

    st.subheader("Extracted Resume Info")
    parsed_data = parse_resume(extracted_text)

    with st.expander("Show Name, Email, Phone, Skills Extracted from resume"):
        st.write("**Name:**", parsed_data["name"])
        st.write("**Email:**", parsed_data["email"])
        st.write("**Phone:**", parsed_data["phone"])
        st.write("**Skills Found:**", parsed_data["skills"])

    experience_level = detect_experience_level(extracted_text)

    st.subheader("Experience Classification")
    st.success(
        f"Based on your resume content, you are classified as **{experience_level}**."
    )

    st.caption(
        "ℹ️ Resume Score is calculated using rule-based heuristics "
        "(sections like skills, experience, projects). "
        "It is used as a baseline quality indicator, not a hiring decision."
    )

    score_data = calculate_resume_score(extracted_text)
    resume_score = score_data["score"]
    score_breakdown = score_data["breakdown"]

    st.subheader("Resume Score")
    st.write(f"Your resume score is **{resume_score} / 100**")

    st.subheader("Resume Score Breakdown")
    for section, points in score_breakdown.items():
        st.write(f"- {section} :: {points} points")

    # ================= ROLE SELECTION =================

    st.subheader("Select Target Job Role")

    available_roles = list(JOB_ROLE_DESCRIPTIONS.keys())
    target_role = st.selectbox(
        "Choose the role you are targeting",
        available_roles
    )

    if "last_selected_role" not in st.session_state:
        st.session_state["last_selected_role"] = target_role

    if st.session_state["last_selected_role"] != target_role:
        st.session_state["analytics_saved"] = False
        st.session_state["last_selected_role"] = target_role

    confirm_analysis = st.button("Confirm")

    # ================= SKILL GAP & MATCH (MODIFIED) =================

    if confirm_analysis:

        st.caption(
            "ℹ️ Skill Gap Analysis compares your resume skills with the selected job role. "
            "Missing skills indicate areas to improve, not disqualification."
        )

        required_skills = ROLE_SKILLS.get(target_role, [])
        resume_skills = normalize_skills(parsed_data.get("skills", []))

        if resume_skills:
            skill_gap = analyze_skill_gap(resume_skills, required_skills)
            present_skills = skill_gap["present_skills"]
            missing_skills = skill_gap["missing_skills"]
        else:
            present_skills = []
            missing_skills = []

        # ======== UPDATED PRESENT SKILLS UI =========
        st.subheader("Skill Gap Analysis")

        st.markdown("### → Your Current Skills")

        if present_skills:
            skill_tags = " ".join(
                [
                    f"<span style='background-color:#32CD32;color:white;padding:6px 10px;"
                    f"border-radius:12px;margin:4px;display:inline-block;'>{skill}</span>"
                    for skill in present_skills
                ]
            )
            st.markdown(skill_tags, unsafe_allow_html=True)
        else:
            st.info("No matching skills found")

        # ======== UPDATED MISSING SKILLS UI =========
        st.markdown("### → Recommended Skills for You")

        if missing_skills:
            missing_tags = " ".join(
                [
                    f"<span style='background-color:#ff6b6b;color:white;padding:6px 10px;"
                    f"border-radius:12px;margin:4px;display:inline-block;'>{skill}</span>"
                    for skill in missing_skills
                ]
            )
            st.markdown(missing_tags, unsafe_allow_html=True)
        else:
            st.success("No missing skills 🎉")

        semantic_text = build_semantic_resume_text(
            raw_text=extracted_text,
            skills=resume_skills,
            experience_level=experience_level
        )
        resume_embedding = get_embedding(semantic_text)

        job_description = JOB_ROLE_DESCRIPTIONS.get(target_role, "")

        @st.cache_data(show_spinner=False)
        def get_cached_job_embedding(description: str):
            return get_embedding(description)

        job_embedding = get_cached_job_embedding(job_description)

        match_score = cosine_similarity(resume_embedding, job_embedding)

        st.subheader("Job Match Score")
        st.write(f"{round(match_score * 100, 2)} %")

        analytics_record = {
            "timestamp": datetime.now(),
            "experience_level": experience_level,
            "resume_score": resume_score,
            "target_role": target_role,
            "job_match_score": match_score,
            "skills_present_count": len(present_skills),
            "skills_missing_count": len(missing_skills)
        }

        if not st.session_state["analytics_saved"]:
            st.session_state["admin_analytics"].append(analytics_record)
            st.session_state["analytics_saved"] = True
