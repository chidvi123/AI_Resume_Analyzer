import re
import json
import os


# ---------------- EMAIL ----------------
def extract_email(text: str):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group() if match else None


# ---------------- PHONE ----------------
def extract_phone(text: str):
    pattern = r"(\+?\d{1,3}[- ]?)?\d{10}"
    match = re.search(pattern, text)
    return match.group() if match else None


# ---------------- NAME ----------------
def extract_name(text: str):
    lines = text.split("\n")
    for line in lines[:5]:
        line = line.strip()
        if len(line.split()) in [2, 3]:
            if not any(char.isdigit() for char in line):
                return line
    return None


# ---------------- SKILLS ----------------
def extract_skills(text: str, skills_file="data/skills.json"):
    """
    Pure skill extraction:
    - Uses skills.json only
    - Handles dirty PDFs (punctuation, spacing)
    - NO aliases
    - NO normalization
    """

    if not text or not os.path.exists(skills_file):
        return []

    # Load global skills
    with open(skills_file, "r", encoding="utf-8") as f:
        skills_list = json.load(f)

    if not isinstance(skills_list, list):
        return []

    # Normalize resume text ONLY for matching safety
    text_lower = text.lower()
    text_lower = re.sub(r"[^\w\s]", " ", text_lower)   # remove punctuation
    text_lower = re.sub(r"\s+", " ", text_lower)      # collapse spaces
    text_spaced = f" {text_lower} "

    found = set()

    for skill in skills_list:
        skill_l = skill.lower().strip()

        # ignore invalid / garbage skills
        if len(skill_l) < 2:
            continue

        if f" {skill_l} " in text_spaced:
            found.add(skill_l)

    return sorted(found)

# ---------------- PARSER ----------------
def parse_resume(text: str):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text)
    }
