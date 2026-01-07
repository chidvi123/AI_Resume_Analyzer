from collections import Counter
from backend.nlp.resume_registry import get_all_resume_entries
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
    resumes=get_all_resume_entries()
    counter=Counter()

    for r in resumes:
        counter.update(r.get("missing_skills",[]))
    return dict(counter)

def get_rolewise_skill_demand(target_role):
    resumes=get_all_resume_entries()
    counter=Counter()

    for r in resumes:
        if r.get("target_role")==target_role:
            counter.update(r.get("missing_skills",[]))

    return dict(counter)

