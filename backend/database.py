import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

LOGGER = logging.getLogger(__name__)


def load_environment(env_path: str | os.PathLike | None = None) -> None:
    default_path = Path(__file__).resolve().parent / ".env"
    resolved_path = Path(env_path) if env_path is not None else default_path
    load_dotenv(dotenv_path=resolved_path, override=False)

    global MONGO_URI, DATABASE_NAME
    MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"
    DATABASE_NAME = os.getenv("DATABASE_NAME") or "CodeForge"


load_environment()

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

users_collection = db["users"]
problems_collection = db["problems"]
skill_profiles_collection = db["skill_profiles"]
submissions_collection = db["submissions"]
roadmaps_collection = db["roadmaps"]
generated_problems_collection = db["generated_problems"]


async def create_indexes():
    try:
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
    except Exception as exc:
        LOGGER.warning("MongoDB indexes could not be created during startup: %s", exc)