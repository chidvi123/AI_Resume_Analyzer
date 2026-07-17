"""
    Determines candidate experience level using strong resume signals.

    Logic:
    - Work experience sections → Experienced
    - Internship sections → Intermediate
    - Page count used as fallback heuristic
    - Avoids false positives from summary self-claims

    This is a rule-based classifier designed for explainability,
    not a machine learning model.
"""
import re

def detect_experience_level(text: str, num_pages: int | None = None) -> str:
    text = text.lower()
    
    # Stricter patterns using word boundaries to prevent substring matches
    # e.g., \bintern\b prevents matching "international"
    experience_patterns = [
        r"\bwork experience\b",
        r"\bprofessional experience\b",
        r"\bemployment history\b",
        r"\bcareer history\b",
        r"\bworked at\b",
        r"\bfull[- ]time\b",
        r"\bsoftware engineer at\b",
        r"\bdeveloper at\b",
        r"\banalyst at\b",
        r"\bsenior role\b",
        r"\bmanager\b"
    ]
    
    internship_patterns = [
        r"\binternship\b",
        r"\bintern\b",
        r"\btrainee\b",
        r"\bapprenticeship\b"
    ]

    # 1. Check for Experienced signals FIRST
    if any(re.search(pattern, text) for pattern in experience_patterns):
        return "Experienced"

    # 2. If not Experienced, check for Intermediate (Internships) signals
    if any(re.search(pattern, text) for pattern in internship_patterns):
        return "Intermediate"
    
    # 3. Fallback to page count heuristic if no clear keywords are found
    if num_pages is not None:
        if num_pages <= 1:
            return "Fresher"
        elif num_pages == 2:
            return "Intermediate"
        else:
            return "Experienced"
            
    return "Fresher"