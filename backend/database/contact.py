from datetime import datetime
from backend.database.db import get_db

def save_contact_request(name:str,email:str,message:str):
    """
    Save contact / collaboration request to DB.
    """
    db=get_db()
    contact_col=db["contact"]

    record={
        "name":name.strip() if name else "Anonumous",
        "email":email.strip(),
        "message":message.strip(),
        "timestamp":datetime.now()
    }

    contact_col.insert_one(record)

