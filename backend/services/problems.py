from typing import List, Optional, Any, Dict
from bson import ObjectId
from database import problems_collection, generated_problems_collection
from schemas.problems import ProblemResponse
from utils.mongo import normalize_mongo_doc


def _prepare_problem_doc(doc: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize Mongo fields and fill defaults expected by ProblemResponse."""
    normalized = normalize_mongo_doc(doc)
    if not normalized:
        return {}

    normalized.setdefault("subtopic", normalized.get("topic", "General"))
    normalized.setdefault("constraints", [])
    normalized.setdefault("hidden_testcases", [])
    normalized.setdefault("expected_pattern", "")
    normalized.setdefault("expected_time_complexity", "O(N)")
    normalized.setdefault("expected_space_complexity", "O(1)")
    normalized.setdefault("function_name", "solve")
    normalized.setdefault("function_signature", "void solve()")
    normalized.setdefault("return_type", "void")
    normalized.setdefault("parameter_types", [])
    return normalized


def to_problem_response(doc: Dict[str, Any]) -> ProblemResponse:
    return ProblemResponse(**_prepare_problem_doc(doc))


def to_problem_responses(docs: List[Dict[str, Any]]) -> List[ProblemResponse]:
    return [to_problem_response(doc) for doc in docs]

async def get_problem_by_topic(topic: str, user_id: str) -> List[ProblemResponse]:
    problems = await problems_collection.find(
        {
            "topic": topic,
            "$or": [
                {"user_id": None},
                {"user_id": user_id}
            ]
        }
    ).to_list(None)
    
    return to_problem_responses(problems)

async def get_problem_by_id(problem_id: str, user_id: str) -> Optional[ProblemResponse]:
    problem = None

    try:
        problem = await problems_collection.find_one(
            {
                "_id": ObjectId(problem_id),
                "$or": [
                    {"user_id": None},
                    {"user_id": user_id},
                ],
            }
        )
    except Exception:
        pass

    if not problem:
        try:
            problem = await generated_problems_collection.find_one(
                {"_id": ObjectId(problem_id), "user_id": user_id}
            )
        except Exception:
            problem = await problems_collection.find_one(
                {"problem_id": problem_id, "user_id": user_id}
            )

    if not problem:
        return None
    return to_problem_response(problem)

async def get_all_problems(user_id: str) -> List[ProblemResponse]:
    problems = await problems_collection.find(
        {
            "$or": [
                {"user_id": None},
                {"user_id": user_id}
            ]
        }
    ).to_list(None)
    
    return to_problem_responses(problems)
