from datetime import datetime
from backend.database.db import get_db

def save_resume(record:dict):
    db=get_db()
    resumes_col=db["resumes"]
    record["timestamp"]=datetime.now()
    resumes_col.insert_one(record)

def get_resume_by_hash(resume_hash:str):
    db=get_db()
    resumes_col=db["resumes"]

    return resumes_col.find_one(
        {"resume_hash":resume_hash}
    )