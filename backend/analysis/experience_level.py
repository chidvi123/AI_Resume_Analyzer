



def detect_experience_level(text:str,num_pages:int|None=None)->str:
    text=text.lower()

    internship_keywords=[
        "intern","internship","trainee"
    ]

    experience_keywords = [
        "work experience",
        "professional experience",
        "employment",
        "worked at",
        "software engineer at",
        "developer at",
        "analyst at",
        "company",
        "designation",
        "role",
        "experience at",
    ]

    if num_pages is not None:
        if num_pages<=1:
            base_level="Fresher"
        elif num_pages==2:
            base_level="Intermediate"
        else:
            base_level="Experienced"
    else:
        base_level="Fresher"

    if any(word in text for word in internship_keywords):
        return "Intermediate"
     
    if any(word in text for word in experience_keywords):
        return "Experienced"
    
    
    return base_level