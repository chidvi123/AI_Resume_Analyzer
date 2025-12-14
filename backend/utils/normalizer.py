from backend.utils.constants import SKILL_ALIASES

def normalize_skills(skills: list[str]) -> list[str]:
    """
    Normalizes skills by lowercasing, alias mapping, and deduplication.
    """
    if not skills:
        return []

    normalized = set()

    for skill in skills:
        skill_clean = skill.lower().strip()
        skill_clean = SKILL_ALIASES.get(skill_clean, skill_clean)
        normalized.add(skill_clean)

    return sorted(list(normalized))