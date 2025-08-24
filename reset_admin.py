
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/docgen")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database()
users_col = db.users

# Clear all users
users_col.delete_many({})  # ⚠️ This removes all users

# Create fresh admin
users_col.insert_one({
    "username": "Admin",
    "password": "Admin@123",
    "role": "admin"
})

print("✅ Users collection cleared and new admin created!")
