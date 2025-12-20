from backend.database.db import get_db

db=get_db()
print(db.list_collection_names())