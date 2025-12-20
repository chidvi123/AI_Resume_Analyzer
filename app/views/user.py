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
from backend.nlp.embeddings import get_embedding
from backend.utils.job_roles import JOB_ROLE_DESCRIPTIONS
from backend.nlp.similarity import cosine_similarity
from backend.utils.text_cleaner import clean_resume_text
from backend.utils.normalizer import normalize_skills
from backend.utils.sematic_text_builder import build_semantic_resume_text
from backend.recommender.course_recommender import get_recommended_courses
from backend.nlp.resume_registry import add_resume_entry
from backend.nlp.resume_similarity import find_similar_resumes
from backend.database.analytics import save_analytics_record
from backend.database.user_data import save_resume,get_resume_by_hash

# ================================
# MODULE 1: USER RESUME ANALYSIS
# Status: Feature-complete
# ================================

def user_page():

    st.title("User Dashboard..")
    st.write("Please upload your resume in PDF Format to begin analysis.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file is None:
        st.info("Please upload a PDF resume to continue")
        st.stop()

    st.success("Resume uploaded successfully..")

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

    # ================= SKILL GAP & MATCH ========================

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


        #=================Course Recommendation======================#

        courses=get_recommended_courses(target_role)

        with st.expander("📚 Recommended Courses & Certifications"):

            if courses:
                st.markdown("Here are some courses based on your selected job role ::")

                for title,link in courses:
                    st.write(f"-[{title}]({link})")
            else:
                st.info("No recommebdations fot this role yet.")
        
        #====================== calculation of resume score ====================#

        semantic_text = build_semantic_resume_text(
            raw_text=extracted_text,
            skills=resume_skills,
            experience_level=experience_level
        )

        resume_hash=hashlib.sha256(
            semantic_text.encode("utf-8")
        ).hexdigest()

        resume_embedding = get_embedding(semantic_text)
        #==============================================================#
        #saving full resume analysis to DB (one resume per confirm click)
        resume_record={
            "resume_hash":resume_hash,
            "raw_text":extracted_text,
            "semantic_text":semantic_text,

            "parsed_data":{
                "name":parsed_data.get("name"),
                "email":parsed_data.get("email"),
                "phone":parsed_data.get("phone"),
                "skills":resume_skills,
            },

            "experience_level":experience_level,
            "resume_score":resume_score,
            "score_breakdown":score_breakdown,

            "skills_present":present_skills,
            "skills_missing":missing_skills,
            "embedding":resume_embedding.tolist(),
        }
        existing_resume=get_resume_by_hash(resume_hash)

        if existing_resume:
            resume_id = existing_resume["_id"]
        else:
            save_resume(resume_record)
            existing_resume=get_resume_by_hash(resume_hash)
            resume_id=existing_resume["_id"]


        #===========================================================#

        add_resume_entry(embedding=resume_embedding,
                         semantic_text=semantic_text,
                         experience_level=experience_level,
                         target_role=target_role,
                         resume_score=resume_score,
                         skills_present_count=len(present_skills),
                         skills_missing_count=len(missing_skills),
                         missing_skills=missing_skills,
                         present_skills=present_skills
                        )
        
        #finding out similar resumes (temporary in user screen)
        
        similar_resumes=find_similar_resumes(
            current_embedding=resume_embedding,
            top_k=3
        )

        if similar_resumes:
            st.subheader("Similar Resumes in this session ")

            for s in similar_resumes:
                st.write(
                    f"Resume ID {s['resume_id']} | "
                    f"Role: {s['target_role']} | "
                    f"Similarity: {round(s['similarity'] * 100, 2)}%"
                )

        job_description = JOB_ROLE_DESCRIPTIONS.get(target_role, "")

        @st.cache_data(show_spinner=False)
        def get_cached_job_embedding(description: str):
            return get_embedding(description)

        job_embedding = get_cached_job_embedding(job_description)

        match_score = cosine_similarity(resume_embedding, job_embedding)

        st.subheader("Job Match Score")
        st.write(f"{round(match_score * 100, 2)} %")

        analytics_record = {
            "resume_id":resume_id,
            "timestamp": datetime.now(),
            "experience_level": experience_level,
            "resume_score": resume_score,
            "target_role": target_role,
            "job_match_score": match_score,
            "skills_present_count": len(present_skills),
            "skills_missing_count": len(missing_skills)
        }

        save_analytics_record(analytics_record)
            
