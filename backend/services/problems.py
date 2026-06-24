from typing import List, Optional
from bson import ObjectId
from schemas.problems import ProblemResponse
from database import problems_collection

async def get_problem_by_topic(topic: str, user_id: str) -> List[dict]:
    problems = await problems_collection.find(
        {
            "topic": topic,
            "$or": [
                {"user_id": None},
                {"user_id": user_id}
            ]
        }
    ).to_list(None)
    
    for problem in problems:
        problem["id"] = str(problem["_id"])
    return problems

async def get_problem_by_id(problem_id: str, user_id: str) -> Optional[dict]:
    try:
        query = {
            "_id": ObjectId(problem_id),
            "$or": [
                {"user_id": None},
                {"user_id": user_id}
            ]
        }
    except Exception:
        # If problem_id is not a valid ObjectId, search by string ID or custom generated problem_id
        query = {
            "problem_id": problem_id,
            "user_id": user_id
        }
        
    problem = await problems_collection.find_one(query)
    if problem:
        problem["id"] = str(problem["_id"])
    return problem

async def get_all_problems(user_id: str) -> List[dict]:
    problems = await problems_collection.find(
        {
            "$or": [
                {"user_id": None},
                {"user_id": user_id}
            ]
        }
    ).to_list(None)
    
    for problem in problems:
        problem["id"] = str(problem["_id"])
    return problems