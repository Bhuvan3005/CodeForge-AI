from schemas.problems import ProblemCreate,ProblemResponse
from database import problems_collection

async def get_problem_by_topic(topic: str,user_id: str):
    problems =  await problems_collection.find(
        {
            "topic": topic,
            "$or": [
                {"user_id": None},
                {"user_id": user_id}
            ]
        }
    ).to_list(None)
    
    for problem in problems:
        problem["_id"]=str(problem["_id"])
    return problems