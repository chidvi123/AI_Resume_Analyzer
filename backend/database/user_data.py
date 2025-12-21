import numpy as np
from datetime import datetime
from backend.database.db import get_db
from bson import ObjectId

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


def load_all_resumes_for_ml():
    """
    Load all resumes needed for ML tasks (similarity, clustering).

    Returns:
    - resume_ids: list of ObjectId
    - embeddings: numpy array of shape (n_resumes, embedding_dim)
    """

    db=get_db()
    resumes_col=db["resumes"]

    docs=list(
        resumes_col.find(
            {},{"_id":1,"embedding":1}
        )
    )

    resume_ids=[d["_id"] for d in docs]
    embeddings=np.array([d["embedding"] for d in docs])

    return resume_ids,embeddings

def save_cluster_assignments(assignments):
     """
    Persist cluster_id for each resume.

    assignments: list of (resume_id, cluster_id)
    """
     
     db=get_db()
     resumes_col=db["resumes"]

     for resume_id,cluster_id in assignments:
         if isinstance(resume_id,str):
             resume_id = ObjectId(resume_id.replace("ObjectId('", "").replace("')", ""))
         resumes_col.update_one(
             {"_id":resume_id},
             {"$set":{"cluster_id":int(cluster_id)}}
         )


