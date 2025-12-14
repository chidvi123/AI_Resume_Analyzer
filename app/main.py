import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
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

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

def main():
    st.sidebar.title("Navigation")

    page = st.sidebar.selectbox(
        "choose a page",
        ["Home", "User", "Feedback", "Admin", "About"]
    )

    if page == "Home":
        st.title("AI Resume Analyzer Pro..")
        st.write("Welcome Dev! Use the Sidebar to navigate.")

    elif page == "User":
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
        try:
            parsed_data = parse_resume(extracted_text)
        except Exception:
            st.error("Resume parsing failed. Please upload a standard resume format.")
            st.stop()

        with st.expander("Show Name, Email, Phone, Skills Extracted from resume"):
            st.write("**Name:**", parsed_data["name"])
            st.write("**Email:**", parsed_data["email"])
            st.write("**Phone:**", parsed_data["phone"])
            st.write("**Skills Found:**", parsed_data["skills"])

        # experience level
        experience_level = detect_experience_level(extracted_text, num_pages=None)

        st.subheader("Experience Classification")
        st.success(f"Based on your resume content, you are classified as **{experience_level}**.")
        
        # resume score
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

        # ================= ROLE SELECTION (SINGLE SOURCE OF TRUTH) =================

        st.subheader("Select Target Job Role")

        available_roles = list(JOB_ROLE_DESCRIPTIONS.keys())

        target_role = st.selectbox(
            "Choose the role you are targeting",
            available_roles
        )

        # ================= SKILL GAP =================
        st.caption(
        "ℹ️ Skill Gap Analysis compares your resume skills with the selected job role. "
        "Missing skills indicate areas to improve, not disqualification."
         )


        required_skills = ROLE_SKILLS.get(target_role, [])
        resume_skills = normalize_skills(parsed_data.get("skills",[]))

        if resume_skills:
            skill_gap = analyze_skill_gap(resume_skills, required_skills)
            present_skills = skill_gap["present_skills"]
            missing_skills = skill_gap["missing_skills"]
        else:
            present_skills = []
            missing_skills = []

        st.subheader("Skill Gap Analysis")
        st.write("**Skills you have**")

        if present_skills:
            with st.expander("Present Skills"):
                for skill in present_skills:
                    st.write(skill)
        else:
            with st.expander("Present Skills"):
                st.write("No matching skills found")

        st.write("**Skills you Are Missing**")

        if missing_skills:
            with st.expander("Missing Skills"):
                for skill in missing_skills:
                    st.write(skill)
        else:
            with st.expander("Missing Skills"):
                st.write("No missing skills")

        # ================= EMBEDDINGS =================
        
        clean_text=clean_resume_text(extracted_text)

        semantic_text=f"""
        skills:{', '.join(parsed_data.get('skills',[]))}
        experience level:{experience_level}
        resume content :{clean_text}
        """
        resume_embedding = get_embedding(semantic_text)

        job_description = JOB_ROLE_DESCRIPTIONS.get(target_role, "")
        job_embedding = get_embedding(job_description) if job_description else None


        #match score
        st.caption(
        "ℹ️  Job Match Score is generated using NLP embeddings and cosine similarity. "
        "It measures semantic similarity between your resume content and the target job role. "
        "This is an AI-assisted estimate, not an exact accuracy score."
        )


        if resume_embedding is not None and job_embedding is not None:
            match_score = cosine_similarity(resume_embedding, job_embedding)
        else:
            match_score = 0.0

        st.subheader("Job Match Score")
        st.write(f"{round(match_score * 100, 2)} %")

    elif page == "Feedback":
        st.title("Feedback Section")
        st.write("User can submit feedback here")

    elif page == "Admin":
        st.title("Admin Dashboard")
        st.write("Admin analytics & user insights will appear here.")

    elif page == "About":
        st.title("About This Project")
        st.write("Information about the AI resume analyzer.")

if __name__ == "__main__":
    main()
