from backend.database.auth import register_user

result = register_user("admin","admin123","admin")

if result:
    print("Admin user created Successfully")
else:
    print("Admin already exists")
