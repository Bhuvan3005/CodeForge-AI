"""
Submission Routes for CodeForge.

POST /submissions/
Submit code for a problem and run the complete
adaptive learning workflow.
"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from schemas.submissions import (
    SubmissionCreate,
    SubmissionResponse,
)

from services.auth import get_current_user
from agents.mentor import mentor_graph

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"]
)


@router.post(
    "/",
    response_model=SubmissionResponse
)
async def submit_code(
    submission: SubmissionCreate,
    current_user=Depends(get_current_user),
):
    """
    Accept a code submission and execute the
    full LangGraph mentor pipeline.

    Workflow:

    1. Load user profile
    2. Load roadmap
    3. Load problem
    4. Execute code
    5. Analyze complexity/pattern
    6. Detect weaknesses
    7. Generate teaching content
    8. Generate remediation problems
    9. Update mastery scores
    10. Recommend next action
    """

    user_id = str(current_user["_id"])

    initial_state = {
        "user_id": user_id,
        "problem_id": submission.problem_id,
        "submission_code": submission.code,
        "submission_language": submission.language,

        # flags
        "is_remediation": False,

        # execution
        "correct": None,
        "test_results": None,

        # loaded resources
        "problem": None,
        "skill_profile": None,
        "roadmap": None,

        # mentor outputs
        "analysis": None,
        "weakness": None,
        "teaching_material": None,
        "remediation_problems": None,
        "skill_update": None,

        # roadmap
        "next_action": None,

        # optional
        "submission_id": None,
    }

    try:
        final_state = await mentor_graph.ainvoke(
            initial_state
        )

    except Exception as e:
        logger.exception(
            "Mentor pipeline failed for user %s",
            user_id
        )

        raise HTTPException(
            status_code=500,
            detail="Mentor pipeline failed"
        )

    analysis = final_state.get("analysis")
    if not analysis:
        raise HTTPException(
            status_code=500,
            detail="Analysis step failed"
        )

    roadmap_decision = (
        final_state.get("roadmap")
        or final_state.get("next_action")
    )

    return SubmissionResponse(
        submission_id=(
            final_state.get("submission_id")
            or ""
        ),

        correct=analysis.correct,
        tests_passed=analysis.tests_passed,
        tests_total=analysis.tests_total,

        analysis=analysis,

        weakness=final_state.get(
            "weakness"
        ),

        teaching=final_state.get(
            "teaching_material"
        ),

        remediation_problems=final_state.get(
            "remediation_problems"
        ),

        skill_profile=final_state.get(
            "skill_profile"
        ),

        roadmap=roadmap_decision,
    )