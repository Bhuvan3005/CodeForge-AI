from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGO_URI)

db = client[DATABASE_NAME]

users_collection = db["users"]
problems_collection = db["problems"]
skill_profiles_collection = db["skill_profiles"]
submissions_collection = db["submissions"]
roadmaps_collection = db["roadmaps"]
generated_problems_collection = db["generated_problems"]


async def create_indexes():
    # Users
    await users_collection.create_index(
        "email",
        unique=True
    )

    # Skill Profiles
    await skill_profiles_collection.create_index(
        "user_id",
        unique=True
    )

    # Roadmaps
    await roadmaps_collection.create_index(
        "user_id",
        unique=True
    )

    # Problems
    await problems_collection.create_index(
        [("topic", 1), ("subtopic", 1)]
    )

    # Submissions
    await submissions_collection.create_index(
        [("user_id", 1), ("problem_id", 1)]
    )

    await submissions_collection.create_index(
        [("user_id", 1), ("created_at", -1)]
    )

    # Generated Problems
    await generated_problems_collection.create_index(
        [("user_id", 1), ("generated_for", 1)]
    )