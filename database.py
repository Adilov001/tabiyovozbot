from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db.users


async def create_db():
    users.create_index("user_id", unique=True)


async def add_user(user_id, first_name, last_name, gender, phone):
    users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "first_name": first_name,
                "last_name": last_name,
                "gender": gender,
                "phone": phone
            }
        },
        upsert=True
    )
