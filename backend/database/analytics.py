from backend.database.db import get_db

def save_analytics_record(record:dict):
    db=get_db() #get MongoDB database
    analytics_col=db["analytics"]  #analytics collection
    #analytics is the collection name 
    analytics_col.insert_one(record)