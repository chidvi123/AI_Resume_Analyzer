from pymongo import MongoClient

_client = None
_db = None

def get_db():
    global _client,_db
    if _db is not None:
        return _db
    
    _client=MongoClient("mongodb://localhost:27017")
    _db=_client["ai_resume_analyzer"] #selecting a specific database called "ai_resume_analyzer"
    return _db