import streamlit as st
from datetime import datetime

def _init_registry():
    if "resume_registry" not in st.session_state:
        st.session_state["resume_registry"]=[]

def add_resume_entry(
          embedding,
          semantic_text,
          experience_level,
          target_role,
          resume_score,
          skills_present_count,
          skills_missing_count,
          missing_skills,
          present_skills,
    ):
        _init_registry()

        resume_id=len(st.session_state["resume_registry"])+1

        record={
            "resume_id":resume_id,
            "timestamp":datetime.now(),
            "embedding":embedding,
            "semantic_text":semantic_text,
            "experience_level":experience_level,
            "target_role":target_role,
            "resume_score":resume_score,
            "skills_present_count":skills_present_count,
            "skills_missing_count":skills_missing_count,
            "missing_skills":missing_skills,
            "present_skills":present_skills
        }

        st.session_state["resume_registry"].append(record)

def get_all_resume_entries():
     _init_registry()
     return st.session_state["resume_registry"]

def get_all_embeddings():
     _init_registry()
     return [r["embedding"] for r in st.session_state["resume_registry"]]

def clear_registry():
     st.session_state["resume_registry"]=[]