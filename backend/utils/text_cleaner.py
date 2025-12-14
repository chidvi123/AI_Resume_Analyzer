import re

def clean_resume_text(text:str)->str:
    if not  text:
        return ""
    
    text=text.lower()

    text=re.sub(r"\S+@\S+"," ",text) #remove emails
    text=re.sub(r"\+?\d[\d\s\-]{8,}\d", " ", text) #removing numbers
    text=re.sub(r"\s+"," ",text) #removes extra whitespaces

    return text.strip()