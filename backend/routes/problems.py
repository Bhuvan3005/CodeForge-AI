from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Union
from bson import ObjectId
from bson.errors import InvalidId

from schemas.problems import ProblemResponse
from services.problems import get_problem_by_topic, get_problem_by_id, get_all_problems
from services.auth import get_current_user

router = APIRouter(prefix="/problems", tags=["Problems"])

@router.get("", response_model=List[ProblemResponse])
async def list_problems(
    current_user=Depends(get_current_user)
):
    """List all problems available to the user."""
    return await get_all_problems(str(current_user["_id"]))

@router.get("/topic/{topic}", response_model=List[ProblemResponse])
async def get_problems_by_topic_route(
    topic: str,
    current_user=Depends(get_current_user)
):
    """Get problems in a specific topic."""
    return await get_problem_by_topic(topic, str(current_user["_id"]))

@router.get("/{topic_or_id}", response_model=Union[ProblemResponse, List[ProblemResponse]])
async def get_problems_or_single(
    topic_or_id: str,
    current_user=Depends(get_current_user)
):
    """
    Fallback routing to satisfy Streamlit's GET /problems/{topic} 
    and general GET /problems/{problem_id} calls.
    """
    user_id = str(current_user["_id"])
    
    is_object_id = False
    try:
        ObjectId(topic_or_id)
        is_object_id = True
    except InvalidId:
        pass
        
    if is_object_id:
        problem = await get_problem_by_id(topic_or_id, user_id)
        if not problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Problem with ID {topic_or_id} not found."
            )
        return problem
    else:
        # Fallback: treat as topic
        return await get_problem_by_topic(topic_or_id, user_id)
