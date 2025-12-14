def analyze_skill_gap(resume_skills, required_skills):

    resume_set = set(resume_skills)
    required_set = set(required_skills)

    present_skills = sorted(list(resume_set & required_set))
    missing_skills = sorted(list(required_set - resume_set))

    return {
        "present_skills": present_skills,
        "missing_skills": missing_skills
    }
