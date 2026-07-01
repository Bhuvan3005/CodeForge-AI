    
#######################################

"""
LangGraph mentor nodes.

Each function represents one node in the mentor workflow.

The graph itself is defined in mentor.py.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from bson import ObjectId

from database import (
    generated_problems_collection,
    problems_collection,
    submissions_collection,
)

from services.evaluator import run_tests

from services.roadmap import (
    get_or_create_skill_profile,
    get_or_create_roadmap,
    update_skill_score,
    add_remediation_to_roadmap,
    advance_roadmap,
    recommend_next_problem,
)

from utils.mongo import normalize_mongo_doc

from schemas.submissions import (
    AnalysisResult,
    WeaknessResult,
    TeachingMaterial,
    RemediationProblem,
)

from agents.state import MentorState

from agents.prompts import (
    build_analysis_prompt,
    build_teaching_prompt,
    build_remediation_prompt,
    build_ai_practice_prompt,
)

from agents.llm import call_llm_json

##########################################################

def _get_mastery(
    skill_profile,
    topic: str,
    subtopic: str,
) -> int:
    topic_scores = skill_profile.mastery_scores.get(
        topic,
        {}
    )

    return topic_scores.get(
        subtopic,
        0,
    )


def _difficulty_for_mastery(
    mastery: int,
) -> tuple[str, int]:

    if mastery < 30:
        return "Easy", 3

    if mastery < 60:
        return "Medium", 2

    return "Medium", 1


#################################################3333

def _build_submission_record(
    state: MentorState,
    analysis: AnalysisResult,
):

    return {

        "user_id": state["user_id"],

        "problem_id": state["problem_id"],

        "code": state["submission_code"],

        "language": state["submission_language"],

        "correct": analysis.correct,

        "time_complexity": analysis.time_complexity,

        "space_complexity": analysis.space_complexity,

        "pattern_used": analysis.pattern_used,

        "pattern_expected": analysis.pattern_expected,

        "is_remediation": state.get(
            "is_remediation",
            False,
        ),

        "created_at": datetime.now(
            timezone.utc
        ),
    }
    
    ################################################################
    
def _prepare_generated_problem(
    prob: dict,
    *,
    user_id: str,
    weakness_name: str,
    topic: str,
    subtopic: str,
    difficulty: str,
):

    return {

        "user_id": user_id,

        "generated_for": subtopic,

        "weakness": weakness_name,

        "topic": topic,

        "subtopic": subtopic,

        "title": prob.get(
            "title",
            f"Practice: {weakness_name}",
        ),

        "description": prob.get(
            "description",
            "",
        ),

        "difficulty": prob.get(
            "difficulty",
            difficulty,
        ),

        "function_name": prob.get(
            "function_name",
            "solve",
        ),

        "function_signature": prob.get(
            "function_signature",
            "void solve()",
        ),

        "return_type": prob.get(
            "return_type",
            "void",
        ),

        "parameter_types": prob.get(
            "parameter_types",
            [],
        ),

        "constraints": prob.get(
            "constraints",
            [],
        ),

        "examples": prob.get(
            "examples",
            [],
        ),

        "visible_testcases": prob.get(
            "visible_testcases",
            [],
        ),

        "hidden_testcases": prob.get(
            "hidden_testcases",
            [],
        ),

        "expected_pattern": prob.get(
            "expected_pattern",
            weakness_name,
        ),

        "expected_time_complexity": prob.get(
            "expected_time_complexity",
            "O(N)",
        ),

        "expected_space_complexity": prob.get(
            "expected_space_complexity",
            "O(1)",
        ),

        "reason": prob.get("reason", "Personalized practice for your current weakness"),
        "learning_objective": prob.get(
            "learning_objective",
            "Strengthen your understanding of the intended concept",
        ),
        "status": "Pending",
        "created_at": datetime.now(
            timezone.utc,
        ),
    }


async def _mark_generated_problem_completed(problem_id: str, user_id: str) -> None:
    """Mark a generated problem as completed when the learner solves it correctly."""
    try:
        await generated_problems_collection.update_one(
            {"_id": ObjectId(problem_id), "user_id": user_id},
            {
                "$set": {
                    "status": "Completed",
                    "completed_at": datetime.now(timezone.utc),
                }
            },
        )
    except Exception:
        pass
    
    
    
    
    
###################################################
async def load_user_profile(
    state: MentorState,
) -> Dict[str, Any]:

    user_id = state["user_id"]

    problem_id = state["problem_id"]

    problem = None

    is_remediation = False

    try:

        problem = await problems_collection.find_one(
            {
                "_id": ObjectId(problem_id)
            }
        )

    except Exception:
        pass

    if not problem:

        try:

            problem = await generated_problems_collection.find_one(
                {
                    "_id": ObjectId(problem_id)
                }
            )

            if problem:
                is_remediation = True

        except Exception:
            pass

    if problem:
        normalize_mongo_doc(problem)

    profile = await get_or_create_skill_profile(
        user_id
    )

    roadmap = await get_or_create_roadmap(
        user_id
    )

    return {

        "problem": problem,

        "is_remediation": is_remediation,

        "skill_profile": profile,

        "roadmap": roadmap,
    }
    
    
    
    
    
    
###########################################

async def submission_analysis(
    state: MentorState,
) -> Dict[str, Any]:

    problem = state["problem"]

    code = state["submission_code"]

    language = state["submission_language"]

    test_results = run_tests(

        code=code,

        language=language,

        function_name=problem.get(
            "function_name",
            "solve",
        ),

        visible_testcases=problem.get(
            "visible_testcases",
            [],
        ),

        hidden_testcases=problem.get(
            "hidden_testcases",
            [],
        ),

        parameter_types=problem.get(
            "parameter_types",
            [],
        ),

        return_type=problem.get(
            "return_type",
            "auto",
        ),
    )

    prompt = build_analysis_prompt(

        problem=problem,

        code=code,

        language=language,

        test_results={

            "passed": test_results["tests_passed"],

            "failed":
                test_results["tests_total"]
                - test_results["tests_passed"],

            "correct":
                test_results["correct"],
        },
    )

    analysis = await call_llm_json(
        prompt,
        temperature=0.2,
    )

    if analysis is None:

        analysis = {

            "time_complexity": "Unknown",

            "space_complexity": "Unknown",

            "pattern_used": "Unknown",

            "pattern_expected": "Unknown",

            "optimal": True,

            "optimization_reason": "",
        }

    model = AnalysisResult(

        correct=test_results["correct"],

        tests_passed=test_results["tests_passed"],

        tests_total=test_results["tests_total"],

        time_complexity=analysis.get(
            "time_complexity",
            "Unknown",
        ),

        expected_time_complexity=problem.get(
            "expected_time_complexity",
            "O(N)",
        ),

        space_complexity=analysis.get(
            "space_complexity",
            "Unknown",
        ),

        expected_space_complexity=problem.get(
            "expected_space_complexity",
            "O(1)",
        ),

        pattern_used=analysis.get(
            "pattern_used",
            "Unknown",
        ),

        pattern_expected=problem.get(
            "expected_pattern",
            "Unknown",
        ),

        topic=problem.get(
            "topic",
            "Unknown",
        ),

        subtopic=problem.get(
            "subtopic",
            "Unknown",
        ),

        optimization_possible=not analysis.get(
            "optimal",
            True,
        ),

        optimization_reason=analysis.get(
            "optimization_reason",
            "",
        ),

        # Phase 4 – Strengths & Weaknesses
        strengths=analysis.get("strengths", []),
        weaknesses=analysis.get("weaknesses", []),
    )

    result = await submissions_collection.insert_one(

        _build_submission_record(
            state,
            model,
        )
    )
    print("Analysis Prompt:", len(prompt))

    return {

        "submission_id": str(
            result.inserted_id
        ),

        "correct": test_results["correct"],

        "test_results": test_results,

        "analysis": model,
    }
    
    
#############################################

def _fallback_teaching_material(
    weakness_name: str,
) -> dict:
    """
    Fallback teaching material if the LLM fails.
    """

    return {
        "concept": weakness_name,
        "explanation": (
            f"Review the {weakness_name} pattern "
            "to improve your solution."
        ),
        "why_it_matters": (
            "Choosing the correct algorithmic pattern "
            "reduces complexity and improves scalability."
        ),
        "example": (
            "// Practice the optimal pattern "
            "using similar problems."
        ),
        "key_takeaways": [
            f"{weakness_name} is the preferred pattern.",
            "Think about time and space complexity.",
            "Practice similar questions."
        ],
        "common_mistakes": [
            "Using unnecessary nested loops.",
            "Ignoring edge cases.",
            "Using the wrong data structure."
        ],
        "optimization_tip": (
            "Look for opportunities to remove "
            "redundant work."
        ),
    }
    
    ############################

def _fallback_remediation_problem(
    weakness_name: str,
    difficulty: str,
) -> dict:
    """
    Fallback remediation problem if the LLM
    fails to generate one.
    """

    return {

        "title": f"Practice: {weakness_name}",

        "description": (
            f"Solve this problem using the "
            f"{weakness_name} pattern."
        ),

        "difficulty": difficulty,

        "function_name": "solve",

        "function_signature": (
            "int solve(vector<int>& nums)"
        ),

        "return_type": "int",

        "parameter_types": [
            "vector<int>"
        ],

        "constraints": [
            "1 <= nums.length <= 1000"
        ],

        "examples": [
            {
                "input": "nums=[1,2,3]",
                "output": "6",
                "explanation": "Sum is 6."
            }
        ],

        "visible_testcases": [
            {
                "input": {
                    "nums": [1,2,3]
                },
                "output": 6
            }
        ],

        "hidden_testcases": [
            {
                "input": {
                    "nums":[5]
                },
                "output":5
            }
        ],

        "expected_pattern": weakness_name,

        "expected_time_complexity":"O(N)",

        "expected_space_complexity":"O(1)",
    }
    
#########################################################

async def get_remediation_history(
    user_id: str,
    topic: str,
    subtopic: str,
) -> dict:
    """
    Fetch previous remediation problems for this user
    so that the LLM avoids generating duplicates.
    """

    generated = await generated_problems_collection.find(
        {
            "user_id": user_id,
            "topic": topic,
            "subtopic": subtopic,
        }
    ).to_list(None)

    titles = []
    descriptions = []
    patterns = []
    completed = []

    for doc in generated:

        titles.append(
            doc.get("title", "")
        )

        descriptions.append(
            doc.get("description", "")
        )

        patterns.append(
            doc.get(
                "expected_pattern",
                "",
            )
        )

        solved = await submissions_collection.find_one(
            {
                "user_id": user_id,
                "problem_id": str(doc["_id"]),
                "correct": True,
            }
        )

        if solved:
            completed.append(
                doc.get("title", "")
            )

    return {

        "titles": titles,

        "completed": completed,

        "descriptions": descriptions,

        "patterns": patterns,
    }
    
#####################################################3

async def weakness_detection(
    state: MentorState,
) -> Dict[str, Any]:
    """
    Detect whether the submission reveals
    a conceptual weakness.
    """

    analysis = state["analysis"]

    problem = state["problem"]

    correct = analysis.correct

    pattern_used = (
        analysis.pattern_used.lower()
    )

    pattern_expected = (
        problem.get(
            "expected_pattern",
            "unknown",
        ).lower()
    )

    weakness_detected = False

    weakness = None

    reason = None

    severity = None

    detected_weakness_str = None
    if getattr(analysis, "weaknesses", None) and len(analysis.weaknesses) > 0:
        valid_weaknesses = [w for w in analysis.weaknesses if "No significant" not in w]
        if valid_weaknesses:
            detected_weakness_str = valid_weaknesses[0]

    if not correct:
        weakness_detected = True
        weakness = detected_weakness_str or problem.get("expected_pattern", "General").title()
        reason = f"Primary issue: {weakness}" if detected_weakness_str else f"Failed {analysis.tests_total-analysis.tests_passed} test case(s)."
        severity = "high"
    elif (
        pattern_used != pattern_expected
        and pattern_used != "unknown"
        and pattern_expected != "unknown"
    ):
        weakness_detected = True
        weakness = detected_weakness_str or pattern_used.title()
        reason = f"Suboptimal approach: {weakness}" if detected_weakness_str else f"Used '{pattern_used}' instead of expected '{pattern_expected}'."
        severity = "medium"
    elif detected_weakness_str:
        # Code was correct and matched pattern, but has minor weakness (e.g. style, space)
        weakness_detected = True
        weakness = detected_weakness_str
        reason = f"Area to improve: {weakness}"
        severity = "low"

    weakness_model = WeaknessResult(

        weakness_detected=weakness_detected,

        weakness=weakness,

        reason=reason,

        severity=severity,

        mastery_delta=(
            -5
            if weakness_detected
            else 15
        ),

        action=(
            "remediation"
            if weakness_detected
            else "continue"
        ),
    )

    return {

        "weakness": weakness_model
    }
    
    ########################################
    
    
async def teaching(
    state: MentorState,
) -> Dict[str, Any]:
        """ Generate personalized teaching material for the detected weakness."""

        problem = state["problem"]

        weakness = state["weakness"]
        analysis = state["analysis"]
        profile = state["skill_profile"]

        mastery = _get_mastery(
            profile,
            problem["topic"],
            problem["subtopic"],
        )

        prompt = build_teaching_prompt(
            problem=problem,
            weakness=weakness.weakness,
            analysis=analysis,
            mastery=mastery,
        )

        material = await call_llm_json(
            prompt,
            temperature=0.3,
        )

        if material is None:
            material = _fallback_teaching_material(
                weakness.weakness
            )

        teaching = TeachingMaterial(

            concept=material.get(
                "concept",
                weakness.weakness,
            ),

            explanation=material.get(
                "explanation",
                "",
            ),

            why_it_matters=material.get(
                "why_it_matters",
                "",
            ),

            example=material.get(
                "example",
                "",
            ),

            key_takeaways=material.get(
                "key_takeaways",
                [],
            ),

            common_mistakes=material.get(
                "common_mistakes",
                [],
            ),

            optimization_tip=material.get(
                "optimization_tip",
                "",
            ),
        )
        print("Teaching Prompt:", len(prompt))

        return {
            "teaching_material": teaching
        }
        
#################################################

async def remediation(
    state: MentorState,
) -> Dict[str, Any]:
    """
    Generate personalized remediation problems
    based on the detected weakness.
    """

    problem = state["problem"]

    profile = state["skill_profile"]

    weakness = state.get("weakness")

    topic = problem["topic"]

    subtopic = problem["subtopic"]

    mastery = _get_mastery(
        profile,
        topic,
        subtopic,
    )

    difficulty, _ = _difficulty_for_mastery(mastery)
    weakness_name = (
        weakness.weakness
        if weakness and getattr(weakness, "weakness_detected", False) and weakness.weakness
        else problem.get("expected_pattern") or problem.get("topic", "General")
    )
    num_problems = 1

    history = await get_remediation_history(
        state["user_id"],
        topic,
        subtopic,
    )

    prompt = build_remediation_prompt(
        problem=problem,
        weakness=weakness_name,
        mastery=mastery,
        history=history,
        num_problems=num_problems,
    )

    generated = await call_llm_json(
        prompt,
        temperature=0.6,
    )

    if (
        generated is None
        or
        not isinstance(generated, list)
    ):

        generated = [

            _fallback_remediation_problem(
                weakness_name,
                difficulty,
            )

        ]

    if generated and isinstance(generated, list):
        generated = [
            prob for prob in generated if isinstance(prob, dict) and prob.get("title")
        ] or generated

    remediation_models = []

    inserted_ids = []

    for prob in generated:

        mongo_doc = _prepare_generated_problem(

            prob,

            user_id=state["user_id"],

            weakness_name=weakness_name,

            topic=topic,

            subtopic=subtopic,

            difficulty=difficulty,
        )

        result = (
            await generated_problems_collection.insert_one(
                mongo_doc
            )
        )

        inserted_ids.append(
            str(result.inserted_id)
        )

        doc = normalize_mongo_doc(
            mongo_doc,
            id_field="problem_id",
        )

        doc["problem_id"] = str(result.inserted_id)

        remediation_models.append(
            RemediationProblem(**doc)
        )

    await add_remediation_to_roadmap(
    state["user_id"],
    inserted_ids,
    )
    print("Remediation Prompt:", len(prompt))

    return {

        "remediation_problems": remediation_models,
        "ai_practice_problem": remediation_models[0] if remediation_models else None,
    }
    
    
##########################################
async def skill_update(
    state: MentorState,
) -> Dict[str, Any]:
    """
    Update the user's mastery score after analysis.
    """

    analysis = state["analysis"]
    problem = state["problem"]
    weakness = state.get("weakness")

    delta = 15

    if weakness and weakness.weakness_detected:
        delta = weakness.mastery_delta

    profile = await update_skill_score(
        user_id=state["user_id"],
        topic=problem["topic"],
        subtopic=problem["subtopic"],
        delta=delta,
        solved=analysis.correct,
        remediation=state.get("is_remediation", False),
    )

    return {
        "skill_profile": profile
    }

async def next_question(
    state: MentorState,
) -> Dict[str, Any]:
    """
    Update the roadmap and recommend the next
    learning action.
    """

    analysis = state["analysis"]

    roadmap = state["roadmap"]

    if analysis.correct:

        await advance_roadmap(
            user_id=state["user_id"],
            problem_id=state["problem_id"],
            correct=analysis.correct,
        )

        await _mark_generated_problem_completed(
            state["problem_id"],
            state["user_id"],
        )

    recommendation = await recommend_next_problem(

        state["user_id"]
    )

    return {

        "next_action": recommendation

    }
    
###############################################

def should_teach(
    state: MentorState,
) -> str:
    """
    Decide whether the workflow should branch
    into teaching/remediation or continue.
    """

    analysis = state.get("analysis")
    weakness = state.get("weakness")

    if analysis and not analysis.correct:
        return "remediation"

    if (

        weakness

        and

        weakness.weakness_detected

    ):
    

        return "teaching"

    return "skill_update"


########################################
# Phase 2 – AI Practice after correct submission
########################################

async def generate_ai_practice(
    state: MentorState,
) -> Dict[str, Any]:
    """
    Generate one harder AI practice problem when the learner
    solves a problem correctly.  The generated problem is stored
    in generated_problems_collection and returned in the state.
    """

    problem = state["problem"]
    profile = state["skill_profile"]
    roadmap = state["roadmap"]
    weakness_model = state.get("weakness")
    
    topic = problem.get("topic", "General")
    subtopic = problem.get("subtopic", "General")

    mastery = _get_mastery(profile, topic, subtopic)
    current_difficulty = roadmap.difficulty if roadmap else "Easy"

    history = await get_remediation_history(
        state["user_id"],
        topic,
        subtopic,
    )

    prompt = build_ai_practice_prompt(
        problem=problem,
        mastery=mastery,
        history=history,
        current_difficulty=current_difficulty,
    )

    generated = await call_llm_json(prompt, temperature=0.6)

    # Accepted submissions should follow the harder-follow-up path and use the
    # current problem's intended concept rather than any weakness text.
    concept = problem.get("expected_pattern") or problem.get("topic", "General")
    if weakness_model and weakness_model.weakness_detected:
        concept = weakness_model.weakness or concept
    weakness_name = concept

    if (
        generated is None
        or not isinstance(generated, list)
        or len(generated) == 0
    ):
        # Fallback if LLM fails
        prob = _fallback_remediation_problem(weakness_name, current_difficulty)
    else:
        prob = generated[0]

    # Map display difficulty label to valid schema Literal
    difficulty_map = {"Easy+": "Easy", "Medium+": "Medium", "Hard": "Hard", "Easy": "Easy", "Medium": "Medium"}
    stored_difficulty = difficulty_map.get(
        prob.get("difficulty", current_difficulty),
        "Medium",
    )

    if not prob.get("reason"):
        prob["reason"] = (
            f"You solved the current problem correctly. This challenge introduces one additional {weakness_name} concept to deepen your mastery."
        )
    if not prob.get("learning_objective"):
        prob["learning_objective"] = (
            f"Practice a slightly harder {weakness_name} variation that builds on the current problem."
        )
    if not prob.get("title") or str(prob.get("title", "")).lower().startswith("practice"):
        prob["title"] = f"{topic} Extension"

    mongo_doc = _prepare_generated_problem(
        prob,
        user_id=state["user_id"],
        weakness_name=weakness_name,
        topic=topic,
        subtopic=subtopic,
        difficulty=stored_difficulty,
    )

    result = await generated_problems_collection.insert_one(mongo_doc)

    doc = normalize_mongo_doc(mongo_doc, id_field="problem_id")
    doc["problem_id"] = str(result.inserted_id)

    try:
        ai_practice = RemediationProblem(**doc)
    except Exception:
        ai_practice = None

    return {"ai_practice_problem": ai_practice}


def should_generate_ai_practice(
    state: MentorState,
) -> str:
    """
    After skill_update, decide whether to generate AI practice.
    Always generate AI practice for correct submissions.
    """
    analysis = state.get("analysis")

    if analysis and analysis.correct:
        return "generate_ai_practice"

    return "next_question"
