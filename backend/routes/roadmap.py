"""
Roadmap Routes for CodeForge.

Provides endpoints for the frontend to query the user's current
learning roadmap, skill profile, and any pending remediation problems.
"""

from fastapi import APIRouter, Depends
from typing import List, Optional
from services.auth import get_current_user
from services.roadmap import get_or_create_skill_profile, get_or_create_roadmap
from database import generated_problems_collection
from schemas.submissions import SkillProfile, Roadmap, RemediationResponse, RemediationProblem

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])


@router.get("/profile", response_model=SkillProfile)
async def get_skill_profile(
    current_user=Depends(get_current_user),
):
    """Get the current user's skill profile with all mastery scores."""
    user_id = str(current_user["_id"])
    profile = await get_or_create_skill_profile(user_id)
    return profile


@router.get("/status", response_model=Roadmap)
async def get_roadmap_status(
    current_user=Depends(get_current_user),
):
    """Get the current user's roadmap status (current topic, progress, etc.)."""
    user_id = str(current_user["_id"])
    roadmap = await get_or_create_roadmap(user_id)
    return roadmap


@router.get("/remediation", response_model=RemediationResponse)
async def get_remediation_problems(
    current_user=Depends(get_current_user),
):
    """
    Get the user's pending remediation problems.
    Returns a list of generated problems that the user must solve
    before continuing the main roadmap.
    """
    user_id = str(current_user["_id"])
    roadmap = await get_or_create_roadmap(user_id)

    queue = roadmap.remediation_queue
    if not queue:
        return {
            "remediation_active": False,
            "active_problem_id": None,
            "problems": []
        }

    from bson import ObjectId
    problems = []
    for pid in queue:
        try:
            prob = await generated_problems_collection.find_one({"_id": ObjectId(pid)})
            if prob:
                prob["problem_id"] = str(prob["_id"])
                # Populate mock/default values for any missing fields to guarantee schema validation
                prob.setdefault("expected_pattern", "")
                prob.setdefault("expected_time_complexity", "")
                prob.setdefault("expected_space_complexity", "")
                prob.setdefault("examples", [])
                prob.setdefault("visible_testcases", [])
                prob.setdefault("hidden_testcases", [])
                problems.append(prob)
        except Exception:
            continue

    return {
        "remediation_active": True,
        "active_problem_id": roadmap.active_remediation,
        "problems": problems,
    }

from schemas.submissions import DashboardResponse

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user=Depends(get_current_user),
):
    """Fetch dashboard statistics and status for the user."""
    user_id = str(current_user["_id"])
    profile = await get_or_create_skill_profile(user_id)
    roadmap = await get_or_create_roadmap(user_id)
    
    return {
        "problems_solved": profile.stats.problems_solved,
        "problems_failed": profile.stats.problems_failed,
        "remediation_completed": profile.stats.remediation_completed,
        "mastery_scores": profile.mastery_scores,
        "current_topic": roadmap.current_topic,
        "current_subtopic": roadmap.current_subtopic,
        "active_problem_id": roadmap.active_problem_id,
        "active_remediation_id": roadmap.active_remediation,
    }
