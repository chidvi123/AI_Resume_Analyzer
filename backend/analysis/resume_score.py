def calculate_resume_score(text: str) -> dict:

    text = text.lower()

    score = 0
    breakdown = {}

    rules = {
        "Summary/Objective": {
            "keywords": ["summary", "objective"],
            "points": 10
        },
        "Education": {
            "keywords": ["education", "degree", "college", "university"],
            "points": 15
        },
        "Skills": {
            "keywords": ["skills", "technologies", "tools"],
            "points": 20
        },
        "Projects": {
            "keywords": ["project", "projects"],
            "points": 20
        },
        "Experience/Internship": {
            "keywords": ["work experience", "experience", "internship"],
            "points": 25
        },
        "Certification": {
            "keywords": ["certifications", "certificate"],
            "points": 10
        }
    }

    real_experience_keywords = [
        "work experience",
        "professional experience",
        "worked at",
        "employment",
        "experience at",
        "intern at",
        "software intern",
        "engineering intern"
    ]

    training_keywords = [
        "certification",
        "training",
        "course",
        "learning",
        "program",
        "springboard",
        "coursera",
        "udemy"
    ]

    for section, rule in rules.items():

        if section == "Experience/Internship":

            has_real_exp = any(k in text for k in real_experience_keywords)
            has_intern = "intern" in text or "internship" in text
            has_training = any(k in text for k in training_keywords)

            if has_real_exp:
                breakdown[section] = rule["points"]
                score += rule["points"]

            elif has_intern and not has_training:
                breakdown[section] = rule["points"] // 2
                score += rule["points"] // 2

            else:
                breakdown[section] = 0

        else:
            if any(keyword in text for keyword in rule["keywords"]):
                breakdown[section] = rule["points"]
                score += rule["points"]
            else:
                breakdown[section] = 0

    if len(text.split()) < 150:
        score -= 10

    score = max(0, min(score, 100))

    return {
        "score": score,
        "breakdown": breakdown
    }
