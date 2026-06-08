from fastapi import APIRouter,Depends
from services.problems import get_problem_by_topic
from services.auth import get_current_user

router=APIRouter(prefix="/problems",tags=["Problems"])

@router.get("/{topic}")
async def get_problems(
    topic: str,
    current_user=Depends(get_current_user)
):
    return await get_problem_by_topic(
        topic,
        str(current_user["_id"])
    )
    
