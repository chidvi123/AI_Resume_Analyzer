import bcrypt
from backend.database.db import get_db

def register_user(username,password,role):
    db=get_db()
    users=db["users"]
    
    if users.find_one({"username":username}):
        return False

    password_hash=bcrypt.hashpw(password.encode(),bcrypt.gensalt())

    users.insert_one({
        "username":username,
        "password_hash":password_hash,
        "role":role
    })

    return True

def verify_user(username,password):
    db=get_db()
    user=db["users"].find_one({"username":username})

    if not user:
        return None
    
    if bcrypt.checkpw(password.encode(),user["password_hash"]):
        return user
    return None

def get_user_by_username(username):
    db=get_db()
    return db['users'].find_one({"username":username})
