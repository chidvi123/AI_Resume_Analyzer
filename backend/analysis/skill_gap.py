from collections import Counter
from backend.database.db import get_db
from backend.utils.normalizer import normalize_skills

def analyze_skill_gap(resume_skills, required_skills):

    resume_set = set(normalize_skills(resume_skills))
    required_set = set(normalize_skills(required_skills))

    present_skills = sorted(list(resume_set & required_set))
    missing_skills = sorted(list(required_set - resume_set))

    return {
        "present_skills": present_skills,
        "missing_skills": missing_skills
    }

def get_global_skill_demand():
    db = get_db()
    resumes = list(db["resumes"].find({}, {"skills_missing": 1}))
    counter = Counter()
    for r in resumes:
        counter.update(r.get("skills_missing", []))
    return dict(counter)

def get_rolewise_skill_demand(target_role):
    db = get_db()
    # analytics collection stores target_role per analysis event
    analytics = list(db["analytics"].find(
        {"target_role": target_role},
        {"resume_id": 1}
    ))
    resume_ids = [a["resume_id"] for a in analytics]
    resumes = list(db["resumes"].find(
        {"_id": {"$in": resume_ids}},
        {"skills_missing": 1}
    ))
    counter = Counter()
    for r in resumes:
        counter.update(r.get("skills_missing", []))
    return dict(counter)

