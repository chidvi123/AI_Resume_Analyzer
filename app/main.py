import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))



import streamlit as st
from backend.utils.helpers import save_uploaded_file,show_pdf
from backend.parser.pdf_reader import extract_text_from_pdf
from backend.parser.resume_parser import parse_resume
from backend.analysis.experience_level import detect_experience_level
from backend.analysis.resume_score import calculate_resume_score
from backend.analysis.skill_gap import analyze_skill_gap
from backend.utils.constants import ROLE_SKILLS



st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

def main():
    st.sidebar.title("Navigation")

    page=st.sidebar.selectbox(
        "choose a page",
        ["Home","User","Feedback","Admin","About"]
    )

    if page=="Home":
        st.title("AI Resume Analyzer Pro..")
        st.write("Welcome Dev! Use the Sidebar to navigate.")

    elif page=="User":
        st.title("User Dashbaord..")

        st.write("Please upload your resume in PDF Format to begin analysis.")

        uploaded_file=st.file_uploader("Uplaod PDF",type=["pdf"])

        if uploaded_file is not None:
            st.success("Resume uploaded successfully..")
            
            file_path=save_uploaded_file(uploaded_file)

            st.write("File saved at :",file_path)

            st.subheader("Preview")
            show_pdf(file_path)

            st.subheader("Extracted text from PDF")
            extracted_text=extract_text_from_pdf(file_path)

            with st.expander("Show extracted text"):
                st.write(extracted_text)

            st.subheader("Extracted Resume Info")
            parsed_data=parse_resume(extracted_text)

            with st.expander("Show Name,Email,Ph no,Skills Extracted from resume"):
                st.write("**Name:**", parsed_data["name"])
                st.write("**Email:**", parsed_data["email"])
                st.write("**Phone:**", parsed_data["phone"])
                st.write("**Skills Found:**", parsed_data["skills"])
            
           #experience_level

            if extracted_text:
                experience_level=detect_experience_level(extracted_text,num_pages=None)
            else:
                experience_level="Unknown"

            st.subheader("Experience Classification")
            st.success(f"Based on your resume content,you are classified as **{experience_level}**.")

            #resume score
            if extracted_text:
                score_data=calculate_resume_score(extracted_text)
                resume_score=score_data["score"]
                score_breakdown=score_data["breakdown"]
            else:
                resume_score=0
                score_breakdown={}
            
            st.subheader("Resume Score")
            st.write(f"Your resume score is **{resume_score} /100**")

            st.subheader("Resume Score Breakdown")
            for section,points in score_breakdown.items():
                st.write(f"- {section} :: {points} points")

            #skill gap

            target_role="data_scientist" #just for now
            required_skills = ROLE_SKILLS.get(target_role,[])

            #skill gap analysis

            resume_skills =parsed_data["skills"]

            if resume_skills:
                skill_gap=analyze_skill_gap(resume_skills,required_skills)
                present_skills=skill_gap["present_skills"]
                missing_skills=skill_gap["missing_skills"]
            else:
                present_skills=[]
                missing_skills=[]
            
            st.subheader("Skill Gap Analysis")
            st.write("**Skills you have**")

            if present_skills:
                with st.expander("Present Skills"):
                    for skill in present_skills:
                        st.write(f"{skill}")
            else:
                with st.expander("Present Skills"):
                    st.write("No matching skills found")

            st.write("**Skills you Are Missing**")

            if missing_skills:
                with st.expander("Missing Skills"):
                    for skill in missing_skills:
                        st.write(f"{skill}")
            else:
                with st.expander("Missing Skills"):
                    st.write("No missing skills")


            



    elif page=="Feedback":
        st.title("Feedback Section")
        st.write("User can submit feedback here ")
    
    elif page=="Admin":
        st.title("Admin Dashboard")
        st.write("Admin analytics & user insights will appea here.")

    elif page=="About":
        st.title("About This Project")
        st.write("Information about the AI reusme analyzer.")

if __name__=="__main__":
    main()