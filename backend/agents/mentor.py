"""
LangGraph Mentor Workflow for CodeForge.

Orchestrates the submission lifecycle:
  1. Executes submission against test cases (C++ or Python)
  2. Analyzes complexity and algorithmic pattern via Gemini
  3. Detects specific weaknesses
  4. Generates targeted concept explanations (Teaching module)
  5. Generates targeted remediation exercises (Remediation problems)
  6. Updates user mastery profile
  7. Advances and updates the learning roadmap
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

import google.generativeai as genai
from langgraph.graph import StateGraph, END

from agents.state import MentorState
from schemas.submissions import (
    AnalysisResult,
    WeaknessResult,
    TeachingMaterial,
    RemediationProblem,
    SkillUpdateResult,
    RoadmapDecision,
)
from database import (
    problems_collection,
    generated_problems_collection,
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

# ── Gemini Configuration ────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  NODE 1 — Load User Profile
# ═══════════════════════════════════════════════════════════════════════════

async def load_user_profile(state: MentorState) -> Dict[str, Any]:
    """Fetch the problem, skill profile, and roadmap from MongoDB."""
    from bson import ObjectId

    user_id = state["user_id"]
    problem_id = state["problem_id"]

    problem = None
    is_remediation = False

    try:
        problem = await problems_collection.find_one({"_id": ObjectId(problem_id)})
    except Exception:
        pass

    if not problem:
        try:
            problem = await generated_problems_collection.find_one({"_id": ObjectId(problem_id)})
            if problem:
                is_remediation = True
        except Exception:
            pass

    if problem:
        problem["_id"] = str(problem["_id"])

    # Load skill profile and roadmap
    skill_profile = await get_or_create_skill_profile(user_id)
    roadmap = await get_or_create_roadmap(user_id)

    return {
        "problem": problem,
        "is_remediation": is_remediation,
        "skill_profile": skill_profile,
        "roadmap": roadmap,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  NODE 2 — Submission Analysis
# ═══════════════════════════════════════════════════════════════════════════

async def submission_analysis(state: MentorState) -> Dict[str, Any]:
    """
    1. Run user code against test cases via the evaluator.
    2. Use Gemini to analyze time/space complexity and pattern detection.
    """
    problem = state["problem"]
    user_code = state["submission_code"]
    language = state["submission_language"]

    if not problem:
        analysis_fail = AnalysisResult(
            correct=False,
            tests_passed=0,
            tests_total=0,
            time_complexity="Unknown",
            expected_time_complexity="Unknown",
            space_complexity="Unknown",
            expected_space_complexity="Unknown",
            pattern_used="Unknown",
            pattern_expected="Unknown",
            topic="Unknown",
            subtopic="Unknown"
        )
        return {
            "correct": False,
            "test_results": {"correct": False, "tests_passed": 0, "tests_total": 0, "compile_error": "Problem not found", "runtime_error": None},
            "analysis": analysis_fail,
        }

    # Run tests
    visible_tc = problem.get("visible_testcases", [])
    hidden_tc = problem.get("hidden_testcases", [])
    function_name = problem.get("function_name", "solve")
    parameter_types = problem.get("parameter_types", [])
    return_type = problem.get("return_type", "auto")

    test_results = run_tests(
        code=user_code,
        language=language,
        function_name=function_name,
        visible_testcases=visible_tc,
        hidden_testcases=hidden_tc,
        parameter_types=parameter_types,
        return_type=return_type
    )

    # Gemini analysis for complexity and pattern
    analysis_prompt = f"""You are an expert algorithm analyst. Analyze the following code submission for a DSA problem.

Problem Title: {problem.get('title', 'Unknown')}
Problem Topic: {problem.get('topic', 'Unknown')}
Problem Description: {problem.get('description', '')}

User's Code ({language}):
```{language}
{user_code}
```

Test Results: {test_results['tests_passed']}/{test_results['tests_total']} tests passed.

Respond ONLY with a valid JSON object (no markdown, no code fences) with these exact keys:
{{
    "time_complexity": "O(...)",
    "space_complexity": "O(...)",
    "pattern_used": "the algorithmic pattern/technique the user actually used",
    "pattern_expected": "the optimal/expected algorithmic pattern for this problem"
}}
"""

    try:
        response = model.generate_content(analysis_prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
        gemini_analysis = json.loads(text)
    except Exception:
        gemini_analysis = {
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "pattern_used": "Unknown",
            "pattern_expected": "Unknown",
        }

    analysis_model = AnalysisResult(
        correct=test_results["correct"],
        tests_passed=test_results["tests_passed"],
        tests_total=test_results["tests_total"],
        time_complexity=gemini_analysis.get("time_complexity", "Unknown"),
        expected_time_complexity=problem.get("expected_time_complexity", "O(N)"),
        space_complexity=gemini_analysis.get("space_complexity", "Unknown"),
        expected_space_complexity=problem.get("expected_space_complexity", "O(1)"),
        pattern_used=gemini_analysis.get("pattern_used", "Unknown"),
        pattern_expected=problem.get("expected_pattern", "Unknown"),
        topic=problem.get("topic", "Unknown"),
        subtopic=problem.get("subtopic", "Unknown"),
        optimization_possible=gemini_analysis.get("pattern_used", "").lower() != problem.get("expected_pattern", "").lower(),
        optimization_reason="Pattern can be optimized."
    )

    # Persist the submission record
    submission_record = {
        "user_id": state["user_id"],
        "problem_id": state["problem_id"],
        "code": user_code,
        "language": language,
        "correct": analysis_model.correct,
        "time_complexity": analysis_model.time_complexity,
        "space_complexity": analysis_model.space_complexity,
        "pattern_used": analysis_model.pattern_used,
        "pattern_expected": analysis_model.pattern_expected,
        "is_remediation": state.get("is_remediation", False),
        "created_at": datetime.now(timezone.utc),
    }
    result = await submissions_collection.insert_one(submission_record)

    return {
        "submission_id": str(result.inserted_id),
        "correct": test_results["correct"],
        "test_results": test_results,
        "analysis": analysis_model,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  NODE 3 — Weakness Detection
# ═══════════════════════════════════════════════════════════════════════════

async def weakness_detection(state: MentorState) -> Dict[str, Any]:
    """
    Determine whether the user has a weakness based on the analysis.
    Weakness is detected when:
      - Tests failed
      - Pattern used != Pattern expected (brute force, suboptimal)
    """
    analysis = state["analysis"]
    problem = state["problem"]

    pattern_used = analysis.pattern_used.lower()
    pattern_expected = problem.get("expected_pattern", "Unknown").lower()
    correct = analysis.correct

    weakness_detected = False
    weakness = None
    reason = None
    severity = None

    if not correct:
        weakness_detected = True
        weakness = problem.get("expected_pattern", "General").title()
        reason = f"User's solution failed {analysis.tests_total - analysis.tests_passed} test case(s)."
        severity = "high"
    elif pattern_used != pattern_expected and pattern_expected != "unknown" and pattern_used != "unknown":
        weakness_detected = True
        weakness = problem.get("expected_pattern", "General").title()
        reason = (
            f"User solved the problem using '{analysis.pattern_used}' "
            f"instead of expected optimal '{problem.get('expected_pattern', 'optimal')}' pattern."
        )
        severity = "medium"

    weakness_model = WeaknessResult(
        weakness_detected=weakness_detected,
        weakness=weakness,
        reason=reason,
        severity=severity,
        mastery_delta=-5 if weakness_detected else 15,
        action="remediation" if weakness_detected else "continue"
    )

    return {
        "weakness": weakness_model
    }


# ═══════════════════════════════════════════════════════════════════════════
#  NODE 4 — Teaching
# ═══════════════════════════════════════════════════════════════════════════

async def teaching(state: MentorState) -> Dict[str, Any]:
    """Generate personalized teaching material for the detected weakness."""
    weakness_info = state["weakness"]
    if not weakness_info or not weakness_info.weakness_detected:
        return {"teaching_material": None}

    weakness_name = weakness_info.weakness or "General Concept"
    reason = weakness_info.reason or ""
    problem = state["problem"]

    teaching_prompt = f"""You are an expert DSA tutor. A student just attempted the problem "{problem.get('title', 'a problem')}" 
on the topic "{problem.get('topic', 'DSA')}".

Weakness detected: {weakness_name}
Reason: {reason}

Generate a teaching module. Respond ONLY with a valid JSON object (no markdown, no code fences):
{{
    "concept": "Name of the concept to teach",
    "explanation": "Clear, detailed explanation of the concept and why it's important for this type of problem. Include complexity analysis.",
    "why_it_matters": "Why this concept is key in production software scale",
    "example": "A complete, simple code example demonstrating the concept with comments",
    "key_takeaways": ["takeaway 1", "takeaway 2", "takeaway 3"],
    "common_mistakes": ["mistake 1", "mistake 2"],
    "optimization_tip": "A tip to optimize code using this concept"
}}
"""

    try:
        response = model.generate_content(teaching_prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
        material = json.loads(text)
    except Exception:
        material = {
            "concept": weakness_name,
            "explanation": f"Review the {weakness_name} pattern to improve your solution approach.",
            "why_it_matters": "Optimal memory usage and complexity reduction is vital for backend systems.",
            "example": "// Practice the optimal pattern in your editor.",
            "key_takeaways": [
                f"The {weakness_name} pattern is more efficient for this type of problem",
                "Consider time and space complexity trade-offs",
                "Practice similar problems to reinforce the concept",
            ],
            "common_mistakes": ["Using recursion without memoization", "Incorrect loop index termination"],
            "optimization_tip": "Choose array indexes over heavy map calls."
        }

    teaching_model = TeachingMaterial(**material)
    return {"teaching_material": teaching_model}


# ═══════════════════════════════════════════════════════════════════════════
#  NODE 5 — Remediation Problem Generation
# ═══════════════════════════════════════════════════════════════════════════

async def remediation(state: MentorState) -> Dict[str, Any]:
    """Generate 1-3 targeted practice problems based on the detected weakness."""
    weakness_info = state["weakness"]
    if not weakness_info or not weakness_info.weakness_detected:
        return {"remediation_problems": []}

    weakness_name = weakness_info.weakness or "General"
    problem = state["problem"]
    skill_profile = state["skill_profile"]

    # Determine difficulty based on mastery score
    topic = problem.get("topic", "General")
    subtopic = problem.get("subtopic", "General")
    
    mastery_scores = skill_profile.mastery_scores
    topic_scores = mastery_scores.get(topic, {})
    current_mastery = topic_scores.get(subtopic, 0)

    if current_mastery < 30:
        difficulty = "Easy"
        num_problems = 3
    elif current_mastery < 60:
        difficulty = "Medium"
        num_problems = 2
    else:
        difficulty = "Medium"
        num_problems = 1

    remediation_prompt = f"""You are an expert DSA problem designer. Generate exactly {num_problems} practice problem(s) 
that specifically target the "{weakness_name}" concept/pattern.

Topic: {topic}
Difficulty: {difficulty}
Purpose: Help a student who struggled with {weakness_name} in the context of "{problem.get('title', 'a problem')}"

For each problem in the array, respond ONLY with a valid JSON array (no markdown, no code fences). Each element must have:
{{
    "title": "Problem Title",
    "description": "Clear problem description with constraints",
    "difficulty": "{difficulty}",
    "function_name": "exact_target_function_name",
    "function_signature": "exact_cpp_function_signature",
    "return_type": "cpp_return_type",
    "parameter_types": ["cpp_param_type_1", "cpp_param_type_2"],
    "constraints": ["constraint 1", "constraint 2"],
    "examples": [
        {{"input": "example input description", "output": "expected output", "explanation": "why this is the answer"}}
    ],
    "visible_testcases": [
        {{"input": {{"param1": "value1"}}, "output": "expected_output"}}
    ],
    "hidden_testcases": [
        {{"input": {{"param1": "value1"}}, "output": "expected_output"}}
    ]
}}

Generate ONLY the JSON array, nothing else.
"""

    generated = []
    try:
        response = model.generate_content(remediation_prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
        generated = json.loads(text)
        if not isinstance(generated, list):
            generated = [generated]
    except Exception:
        generated = [
            {
                "title": f"Practice: {weakness_name}",
                "description": f"Solve this problem using the {weakness_name} technique. This is a targeted practice exercise.",
                "difficulty": difficulty,
                "function_name": "solvePractice",
                "function_signature": "int solvePractice(vector<int>& nums)",
                "return_type": "int",
                "parameter_types": ["vector<int>"],
                "constraints": ["nums.size() <= 1000"],
                "examples": [{"input": "nums = [1, 2, 3]", "output": "6", "explanation": "Sum is 6"}],
                "visible_testcases": [{"input": {"nums": [1, 2, 3]}, "output": 6}],
                "hidden_testcases": [{"input": {"nums": [1, 1, 1]}, "output": 3}],
            }
        ]

    # Store generated problems in MongoDB
    stored_problems = []
    stored_ids = []
    for prob in generated:
        doc = {
            "user_id": state["user_id"],
            "generated_for": subtopic,
            "weakness": weakness_name,
            "topic": topic,
            "subtopic": subtopic,
            "title": prob.get("title", f"Practice: {weakness_name}"),
            "description": prob.get("description", ""),
            "difficulty": prob.get("difficulty", difficulty),
            "function_name": prob.get("function_name", "solve"),
            "function_signature": prob.get("function_signature", "void solve()"),
            "return_type": prob.get("return_type", "void"),
            "parameter_types": prob.get("parameter_types", []),
            "constraints": prob.get("constraints", []),
            "examples": prob.get("examples", []),
            "visible_testcases": prob.get("visible_testcases", []),
            "hidden_testcases": prob.get("hidden_testcases", []),
            "expected_pattern": weakness_name,
            "expected_time_complexity": "O(N)",
            "expected_space_complexity": "O(N)",
            "created_at": datetime.now(timezone.utc),
        }
        result = await generated_problems_collection.insert_one(doc)
        problem_id_str = str(result.inserted_id)
        stored_ids.append(problem_id_str)

        stored_problems.append(
            RemediationProblem(
                problem_id=problem_id_str,
                title=doc["title"],
                topic=doc["topic"],
                subtopic=doc["subtopic"],
                difficulty=doc["difficulty"],
                description=doc["description"],
                function_name=doc["function_name"],
                function_signature=doc["function_signature"],
                constraints=doc["constraints"],
                expected_pattern=doc["expected_pattern"],
                expected_time_complexity=doc["expected_time_complexity"],
                expected_space_complexity=doc["expected_space_complexity"],
                examples=doc["examples"],
                visible_testcases=doc["visible_testcases"],
                hidden_testcases=doc["hidden_testcases"],
                generated_for=doc["generated_for"],
                weakness=doc["weakness"],
                user_id=doc["user_id"]
            )
        )

    # Add to user's remediation queue
    await add_remediation_to_roadmap(state["user_id"], stored_ids)

    return {"remediation_problems": stored_problems}


# ═══════════════════════════════════════════════════════════════════════════
#  NODE 6 — Skill Update
# ═══════════════════════════════════════════════════════════════════════════

async def skill_update(state: MentorState) -> Dict[str, Any]:
    """Update the user's mastery scores based on submission results."""
    analysis = state["analysis"]
    weakness_info = state["weakness"]
    problem = state["problem"]
    user_id = state["user_id"]

    topic = problem.get("topic", "General")
    subtopic = problem.get("subtopic", "General")

    if weakness_info and weakness_info.weakness_detected:
        # Penalty
        delta = -5 if not analysis.correct else 2
    else:
        # Improvement
        delta = 15 if analysis.correct else 5

    result = await update_skill_score(user_id, topic, subtopic, delta)
    
    # Reload the latest profile
    updated_profile = await get_or_create_skill_profile(user_id)

    return {
        "skill_update": result,
        "skill_profile": updated_profile
    }


# ═══════════════════════════════════════════════════════════════════════════
#  NODE 7 — Next Question / Roadmap Advancement
# ═══════════════════════════════════════════════════════════════════════════

async def next_question(state: MentorState) -> Dict[str, Any]:
    """Advance the roadmap and recommendation algorithm."""
    user_id = state["user_id"]
    problem_id = state["problem_id"]
    correct = state.get("correct", False)

    # 1. Update completed history in DB
    await advance_roadmap(user_id, problem_id, correct)

    # 2. Recommend next topic/problem
    decision = await recommend_next_problem(user_id)

    return {
        "next_action": decision
    }


# ═══════════════════════════════════════════════════════════════════════════
#  CONDITIONAL EDGE — Route based on weakness detection
# ═══════════════════════════════════════════════════════════════════════════

def should_teach(state: MentorState) -> str:
    """Conditional edge: route to 'teaching' if weakness detected, else 'skill_update'."""
    weakness = state["weakness"]
    if weakness and weakness.weakness_detected:
        return "teaching"
    return "skill_update_optimal"


# ═══════════════════════════════════════════════════════════════════════════
#  BUILD THE GRAPH
# ═══════════════════════════════════════════════════════════════════════════

def build_mentor_graph():
    workflow = StateGraph(MentorState)

    # Add all nodes
    workflow.add_node("load_user_profile", load_user_profile)
    workflow.add_node("submission_analysis", submission_analysis)
    workflow.add_node("weakness_detection", weakness_detection)
    workflow.add_node("teaching", teaching)
    workflow.add_node("remediation", remediation)
    workflow.add_node("skill_update_weak", skill_update)
    workflow.add_node("skill_update_optimal", skill_update)
    workflow.add_node("next_question", next_question)
    workflow.add_node("next_question_optimal", next_question)

    # Set entry point
    workflow.set_entry_point("load_user_profile")

    # Linear edges
    workflow.add_edge("load_user_profile", "submission_analysis")
    workflow.add_edge("submission_analysis", "weakness_detection")

    # Conditional edge from weakness_detection
    workflow.add_conditional_edges(
        "weakness_detection",
        should_teach,
        {
            "teaching": "teaching",
            "skill_update_optimal": "skill_update_optimal",
        },
    )

    # Weakness path
    workflow.add_edge("teaching", "remediation")
    workflow.add_edge("remediation", "skill_update_weak")
    workflow.add_edge("skill_update_weak", "next_question")
    workflow.add_edge("next_question", END)

    # Optimal path
    workflow.add_edge("skill_update_optimal", "next_question_optimal")
    workflow.add_edge("next_question_optimal", END)

    return workflow.compile()


mentor_graph = build_mentor_graph()
