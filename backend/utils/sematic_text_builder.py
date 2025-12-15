"""
Builds a signal-focused semantic representation of resumes
for NLP embeddings.

Design decisions:
- Removes personal identifiers (name, email, phone)
- Emphasizes skills, experience, and project-related content
- Produces consistent input for cosine similarity matching

This separation prevents noise from affecting ML similarity scores.
"""

import re

IMPORTANT_SECTIONS = [
    "experience",
    "work experience",
    "internship",
    "internships",
    "projects",
    "project",
    "skills",
    "technical skills"
]

def build_semantic_resume_text(
    raw_text: str,
    skills: list[str],
    experience_level: str
) -> str:
    if not raw_text:
        return ""

    text = raw_text.lower()

    # Remove emails & phone numbers
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\+?\d[\d\s\-]{8,}\d", " ", text)

    lines = text.splitlines()

    selected_lines = []

    for line in lines:
        if any(section in line for section in IMPORTANT_SECTIONS):
            selected_lines.append(line)
        elif len(line.split()) > 4:
            selected_lines.append(line)

    semantic_text = f"""
    experience_level: {experience_level}
    skills: {', '.join(skills)}
    resume_content:
    {' '.join(selected_lines)}
    """

    semantic_text = re.sub(r"\s+", " ", semantic_text)

    return semantic_text.strip()
