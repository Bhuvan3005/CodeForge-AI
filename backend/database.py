from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGO_URI)

db = client[DATABASE_NAME]

users_collection = db["users"]
progress_collection = db["progress"]
problems_collection=db["problems"]




async def create_indexes():
    await users_collection.create_index("email", unique=True)
    await progress_collection.create_index("user_id", unique=True)
   