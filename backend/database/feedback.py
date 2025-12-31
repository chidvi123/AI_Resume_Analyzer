from datetime import datetime 
from backend.database.db import get_db

def save_feedback(name:str,email:str,rating:int,message:str):
    """
    save user feedback to DB
    Name ,Email,rating,comments(message).
    """

    db=get_db()
    feedback_col=db["feedback"]

    record={
        "name":name.strip() if name else "Anonymous",
        "email":email.strip() if email else None,
        "rating":int(rating),
        "message":message.strip(),
        "timestamp":datetime.now()
    }

    feedback_col.insert_one(record)

def get_recent_feedback(limit:int = 5):
    """
    Fetching recent 5 feedback given by users ,
    """

    db=get_db()
    feedback_col=db["feedback"]

    return list(
        feedback_col.find(
            {},
            {
                "_id":0,
                "name":1,
                "rating":1,
                "message":1,
                "timestamp":1
            }
        ).sort("timestamp",-1).limit(limit)
    )

def get_feedback_rating_stars():
    """
    Returns:
    - average_rating (float)
    - rating_counts (dict: {rating: count})
    """
    db=get_db()
    feedback_col=db["feedback"]

    feedbacks=list(
        feedback_col.find(
            {},
            {
                "rating":1,
                "_id":0
            }
        )
    )

    if not feedbacks:
        return 0.0,{}
    
    ratings=[f["rating"] for f in feedbacks]

    avg_rating=round(sum(ratings)/len(ratings),2)

    rating_counts={}
    for r in ratings:
        rating_counts[r]=rating_counts.get(r,0)+1
    
    return avg_rating,rating_counts
   
    