import re
import json
import os

def extract_email(text:str):
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match=re.search(pattern,text)
    return match.group() if match else None

def extract_phone(text:str):
    pattern = r"(\+?\d{1,3}[- ]?)?\d{10}"
    match=re.search(pattern,text)
    return match.group() if match else None

def extract_name(text:str):
    lines=text.split("\n")
    for line in lines[:5]:
        line =line.strip()
        if len(line.split()) in [2,3]:
            if not any(char.isdigit() for char in line):
                return line
    return None

def extract_skills(text:str,skills_file="data/skills.json"):
    if not os.path.exists(skills_file):
        return []
    
    with open(skills_file,"r") as f:
        skills_list=json.load(f)
    
    text_lower=text.lower()
    found=[]

    for skill in skills_list:
        if skill.lower() in text_lower:
            found.append(skill)

    return list(set(found))

def parse_resume(text:str):
    return{
        "name":extract_name(text),
        "email":extract_email(text),
        "phone":extract_phone(text),
        "skills":extract_skills(text)
    }


