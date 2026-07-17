"""
Resume parsing module.

Extraction strategy:
- Name & Skills: Groq API with llama3 (context-aware, handles messy/non-standard resumes)
- Email & Phone: regex fallback (fast, free, deterministic)

Groq is cached per resume text so the same upload never calls the API twice.
"""

import re
import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


# ─── Groq client ─────────────────────────────────────────────────────────────

def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    return Groq(api_key=api_key)


# ─── AI extraction (cached) ──────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def extract_with_ai(text: str) -> dict:
    """
    Uses Groq (llama-3.1-8b-instant) to extract name and skills from resume text.
    Returns a dict with 'name' and 'skills'.
    Falls back to safe defaults on any error.
    """
    prompt = f"""You are a resume parser. Extract the following from the resume text below.
Return ONLY a valid JSON object with no extra text, no markdown, no explanation.

Fields to extract:
- "name": The candidate's full name (string, or null if not found)
- "skills": A comprehensive list of technical skills, tools, frameworks, languages, and platforms
  mentioned anywhere in the resume. Be thorough — include skills implied by project descriptions
  or experience (e.g. "built a REST API" should include "rest api").
  All skill names must be lowercase.

Resume text:
\"\"\"
{text[:4000]}
\"\"\"

Return exactly this JSON format:
{{
  "name": "...",
  "skills": ["skill1", "skill2", ...]
}}"""

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        return {
            "name": parsed.get("name") or None,
            "skills": [s.lower().strip() for s in parsed.get("skills", []) if s]
        }

    except Exception as e:
        # Graceful fallback — don't crash the app
        return {"name": None, "skills": []}


# ─── Email ───────────────────────────────────────────────────────────────────

def extract_email(text: str):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group() if match else None


# ─── Phone ───────────────────────────────────────────────────────────────────

def extract_phone(text: str):
    pattern = r"(\+?\d{1,3}[- ]?)?\d{10}"
    match = re.search(pattern, text)
    return match.group() if match else None


# ─── Skills (via Groq AI) ─────────────────────────────────────────────────────

def extract_skills(text: str, skills_file=None) -> list[str]:
    """
    Extracts skills using Groq llama3.
    The skills_file param is kept for backward compatibility but unused.
    """
    result = extract_with_ai(text)
    return result.get("skills", [])


# ─── Name (via Groq AI) ───────────────────────────────────────────────────────

def extract_name(text: str):
    result = extract_with_ai(text)
    return result.get("name")


# ─── Main parser ─────────────────────────────────────────────────────────────

def parse_resume(text: str) -> dict:
    """
    Full resume parsing.
    AI call is made once and cached — email/phone use regex.
    """
    ai_data = extract_with_ai(text)

    return {
        "name":   ai_data.get("name"),
        "email":  extract_email(text),
        "phone":  extract_phone(text),
        "skills": ai_data.get("skills", [])
    }
