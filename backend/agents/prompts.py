def _truncate(text, limit=4000):
    """Hard-cap any single string field so prompts can't balloon out of control."""
    if not text:
        return text
    text = str(text)
    return text if len(text) <= limit else text[:limit] + "...[truncated]"


def _truncate_list(items, max_items=5, item_limit=200):
    """Cap both the number of items and each item's length for list-type context."""
    if not items:
        return []
    capped = [ _truncate(i, item_limit) for i in items[:max_items] ]
    if len(items) > max_items:
        capped.append(f"...and {len(items) - max_items} more")
    return capped


def build_analysis_prompt(
    *,
    problem: dict,
    code: str,
    language: str,
    test_results: dict,
):
    code = _truncate(code, 6000)
    description = _truncate(problem.get("description"), 1500)

    return f"""
You are a FAANG technical interviewer. Analyze this code submission's complexity, pattern, strengths and weaknesses.

PROBLEM
Title: {problem.get("title")}
Topic/Subtopic: {problem.get("topic")} / {problem.get("subtopic")}
Description: {description}
Expected Pattern: {problem.get("expected_pattern")}
Expected Complexity: time={problem.get("expected_time_complexity")} space={problem.get("expected_space_complexity")}

SUBMISSION ({language})
```{language}
{code}
```

RESULTS
Passed: {test_results.get("passed")} Failed: {test_results.get("failed")} Correct: {test_results.get("correct")}

RULES
- Base every claim ONLY on the submitted code and test results. Do not hallucinate strengths or weaknesses.
- No markdown, no commentary, no text outside the JSON object below.
- strengths: list 1-4 concise strings of what the learner did CORRECTLY in their actual code (e.g. "Correct algorithm selection", "Optimal time complexity", "Good base case handling"). Never invent strengths unsupported by the code.
- weaknesses: list 1-4 concise strings explaining the actual mistake (e.g. "Incorrect DP transition", "Off-by-one error"). Do not just report failed tests, explain WHY.
- IF the solution is completely correct and optimal, weaknesses MUST exactly be: ["No significant weaknesses detected."]
- IF a valid alternative algorithm is used instead of the expected pattern, acknowledge it and do not mark it as incorrect.

Return STRICT JSON ONLY, exactly this schema:
{{
  "time_complexity": "",
  "space_complexity": "",
  "pattern_used": "",
  "pattern_expected": "",
  "optimal": true,
  "optimization_reason": "",
  "memory_observation": [],
  "loop_observation": [],
  "confidence": 95,
  "strengths": [],
  "weaknesses": []
}}

Return STRICT JSON ONLY.
No markdown.
No explanations.
No comments.
No surrounding text.
No code fences.
"""


def build_teaching_prompt(
    *,
    problem: dict,
    weakness: str,
    analysis: dict,
    mastery: int,
):
    if hasattr(analysis, "model_dump"):
        analysis = analysis.model_dump()

    return f"""
You are a senior FAANG engineer mentoring one student 1:1. Teach ONLY the core idea behind THIS specific problem.
Mastery level: {mastery}/100. Do not teach generic topics (e.g., "What is a Stack?") but explain why the concept works for this exact problem.

CONTEXT
Topic/Subtopic: {problem.get("topic")} / {problem.get("subtopic")}
Weakness: {weakness}
Student Pattern: {analysis.get("pattern_used")} | Expected: {analysis.get("pattern_expected")}
Optimal: {analysis.get("optimal")} — {_truncate(analysis.get("optimization_reason"), 300)}
Memory Issues: {_truncate_list(analysis.get("memory_observation"), 5, 150)}
Loop Issues: {_truncate_list(analysis.get("loop_observation"), 5, 150)}

Cover: intuition, expert thinking process, why brute force fails (tie to actual issues above),
pattern recognition signals, before/after complexity, production use cases, interview tips,
optimization advice, common mistakes, key takeaways, and a short example_code snippet using a
DIFFERENT scenario than the original problem (never reveal the original solution).

Be encouraging but rigorous. Ground claims only in the context above; never invent prior history.

EXAMPLE_CODE FORMAT RULES (CRITICAL)
- "example_code" must be a single JSON string, not nested JSON, not an array, not an object.
- Do NOT wrap it in triple backticks (```).
- Do NOT use any markdown formatting (no headers, no bold, no inline code fences) inside it.
- All newlines inside the code must be escaped as \\n so the string is valid JSON on one line.
- Correct example:
  "example_code":"def fib(n):\\n    a,b=0,1\\n    return a"
- Forbidden:
  - ```python ... ```
  - any triple backticks anywhere in the value
  - markdown formatting of any kind
  - literal unescaped line breaks inside the string

Return STRICT JSON ONLY, exactly this schema:
{{
  "intuition": "",
  "thinking_process": "",
  "why_brute_force_fails": "",
  "pattern_recognition_signals": [],
  "complexity_analysis": "",
  "production_use_cases": [],
  "interview_tips": [],
  "optimization_advice": "",
  "common_mistakes": [],
  "key_takeaways": [],
  "example_code": ""
}}

Return STRICT JSON ONLY.
No markdown.
No explanations.
No comments.
No surrounding text.
No code fences.
"""


def build_remediation_prompt(
    *,
    problem: dict,
    weakness: str,
    mastery: int,
    history: dict,
    num_problems: int,
):
    if mastery < 30:
        difficulty = "Easy"
    elif mastery < 60:
        difficulty = "Medium"
    else:
        difficulty = "Hard"

    titles = _truncate_list(history.get("titles"), 8, 100)
    completed = _truncate_list(history.get("completed"), 8, 100)
    descriptions = _truncate_list(history.get("descriptions"), 5, 200)
    patterns = _truncate_list(history.get("patterns"), 8, 60)

    return f"""
You are a Senior FAANG DSA Curriculum Architect designing the NEXT learning stage for one student.
You are not a random problem generator.

STUDENT STATE
Weakness: {weakness}
Topic/Subtopic: {problem.get("topic")} / {problem.get("subtopic")}
Mastery: {mastery}/100 → Difficulty: {difficulty}
Original Problem: {problem.get("title")}

HISTORY (do not repeat any of this)
Titles: {titles}
Completed: {completed}
Past Descriptions: {descriptions}
Patterns Practiced: {patterns}

PROGRESSION
Reason internally about which stage the student has reached for {weakness}.
Generate exactly ONE easier remediation-focused AI practice problem that isolates the single missing concept.
Never expose this reasoning. Generate only the NEXT unexplored stage(s); never regress to a stage already in history.

NON-DUPLICATION
Every new problem must differ from ALL history entries in: title, scenario, constraints, objective,
testcase structure, and optimal strategy. Never disguise an old concept with new flavor text. Never
produce renamed/re-skinned LeetCode problems.

REQUIREMENTS
- Generate exactly one interview-quality problem with a meaningful title, clear description, correct constraints, at least 2 sample test cases, correct expected outputs, a difficulty level, an expected algorithm, and expected time complexity.
- The problem must be valid and internally consistent, with valid sample test cases and a clearly required algorithm.
- The problem must have exactly one unambiguous interpretation.
- Every variable mentioned in the description must appear in the function signature.
- Every function parameter must appear in every sample input.
- Every sample output must be derivable from the problem statement.
- Hidden test cases must use the exact same function signature.
- The intended algorithm must actually be required; do not generate a problem that is solvable by trivial scanning, O(1) arithmetic, or a greedy shortcut when the topic requires a stronger algorithm.
- The problem must be logically correct, internally consistent, and match its own examples and constraints.
- It must actually require the intended algorithm and feel like a real interview question, not a toy problem.
- Avoid trivial prompts such as finding a middle index, first smaller element, or duplicate in a stack.
- Calibrate constraints/input size/edge cases to "{difficulty}" difficulty and make the problem feel like an original interview question.
- Each problem must be judge-executable: valid function_name, matching function_signature/parameter_types/return_type,
  and visible_testcases + hidden_testcases covering normal, boundary, and edge cases.
- Stay within {weakness} and {problem.get("topic")} unless a natural extension is required.
- Do not fabricate history beyond what's given above.
- Before returning the problem, internally verify: title matches description; constraints match inputs; sample inputs contain every parameter; sample outputs are correct; function signature matches samples; the advertised algorithm is necessary; the solution is unique and unambiguous. If any check fails, regenerate the question before returning it.

FUNCTION SIGNATURE FORMAT (CRITICAL — LANGUAGE-NEUTRAL ONLY)
function_signature must describe the function abstractly, NOT in any specific programming language.
Correct example:
  function_name: "minCoins"
  function_signature: "minCoins(coins, amount)"
  return_type: "int"
  parameter_types: ["list[int]", "int"]
parameter_types must use language-neutral type names: int, float, str, bool, list[int], list[str],
list[list[int]], dict[str,int], etc.
FORBIDDEN in function_name, function_signature, return_type, and parameter_types:
- JavaScript syntax (e.g. "function minCoins(coins, amount) {{ }}")
- the "function" keyword or "{{ }}" braces
- semicolons
- language-specific boilerplate (var/let/const, public/private, includes, imports, type annotations
  like "number" or "string[]" from JS/TS, etc.)

Return EXACTLY 1 problem. Return STRICT JSON ONLY — a JSON array, no markdown, no commentary.
Schema per element:
[
  {{
    "title": "",
    "description": "",
    "difficulty": "{difficulty}",
    "stage": "",
    "function_name": "",
    "function_signature": "",
    "return_type": "",
    "parameter_types": [],
    "constraints": [],
    "examples": [
      {{
        "input": "nums=[2,3,1,1,4]",
        "output": "2",
        "explanation": "..."
      }}
    ],
    "visible_testcases": [
      {{
        "input": {{
          "nums": [2, 3, 1, 1, 4]
        }},
        "output": 2
      }}
    ],
    "hidden_testcases": [
      {{
        "input": {{
          "nums": [10, 20, 30]
        }},
        "output": 3
      }}
    ]
  }}
]

NOTES ON THE FIELDS ABOVE
- "examples" is for human-readable display only. "input" is a string, "output" is ALWAYS a string
  (even for numeric results, e.g. "output":"6"), and "explanation" is MANDATORY — never omit it,
  never leave it empty.
- "visible_testcases" and "hidden_testcases" must be judge-executable. "input" MUST ALWAYS be a
  JSON OBJECT whose keys exactly match the function's parameter names — never a string.
  Correct:   {{"input": {{"nums": [1, 2, 3]}}, "output": 6}}
  Forbidden: {{"input": "[1,2,3]", "output": 6}}
  "output" in these two fields is the literal expected return value in its real type (number, string,
  array, etc.), not a string description.
- Include several visible_testcases (normal + obvious edge cases) and several hidden_testcases
  (boundary/edge cases) per problem, following this exact shape.

Return STRICT JSON ONLY.
No markdown.
No explanations outside the JSON.
No comments.
No surrounding text.
No code fences.
"""


def build_ai_practice_prompt(
    *,
    problem: dict,
    mastery: int,
    history: dict,
    current_difficulty: str,
):
    """
    Build a prompt that generates ONE harder AI practice problem
    after a learner successfully solves a curated problem.
    """
    titles = _truncate_list(history.get("titles"), 8, 100)
    completed = _truncate_list(history.get("completed"), 8, 100)
    descriptions = _truncate_list(history.get("descriptions"), 5, 200)
    patterns = _truncate_list(history.get("patterns"), 8, 60)

    # Step up difficulty label
    difficulty_ladder = {
        "Easy": "Easy",
        "Medium": "Medium",
        "Hard": "Hard",
    }
    next_difficulty = difficulty_ladder.get(current_difficulty, "Medium")

    return f"""
You are a Senior FAANG DSA Curriculum Architect. A student just CORRECTLY solved a problem.
Generate exactly ONE follow-up AI practice problem that is slightly harder and introduces ONE additional concept.

STUDENT STATE
Original Problem: {problem.get("title")}
Topic/Subtopic: {problem.get("topic")} / {problem.get("subtopic")}
Pattern Practiced: {problem.get("expected_pattern")}
Mastery: {mastery}/100
Target Difficulty: {next_difficulty} (one step harder than {current_difficulty})

HISTORY (do not repeat or re-skin any of these)
Titles: {titles}
Completed: {completed}
Past Descriptions: {descriptions}
Patterns Practiced: {patterns}

REQUIREMENTS
- Same topic as the original, slightly more difficult, introduces ONE new concept
- Must not duplicate the original problem or any history entry in title, scenario, or strategy
- Must be interview-quality and internally consistent, with a meaningful title, clear description, correct constraints, at least 2 sample test cases, valid sample test cases, correct sample inputs/outputs, and an expected algorithm
- The problem must have exactly one unambiguous interpretation.
- Every variable mentioned in the description must appear in the function signature.
- Every function parameter must appear in every sample input.
- Every sample output must be derivable from the problem statement.
- Hidden test cases must use the exact same function signature.
- Must actually require the intended algorithm rather than being solvable by a trivial scan or shortcut. If the topic is Binary Search, the solution must genuinely require Binary Search; if it is Dynamic Programming, the optimal solution must genuinely require DP. The required algorithm must be explicit and necessary.
- Do not use weakness text, complexity messages, or analysis feedback as the title, reason, or learning objective
- The target concept must be a DSA concept such as Dynamic Programming, Binary Search, Two Pointers, or Graph Traversal
- The title should describe a fresh interview-style challenge, not a generic practice label
- The reason and learning_objective fields should describe conceptual growth from the solved problem
- Must be judge-executable: valid function_name, matching function_signature/parameter_types/return_type
- Include visible_testcases + hidden_testcases covering normal, boundary, and edge cases
- Before returning the problem, internally verify: title matches description; constraints match inputs; sample inputs contain every parameter; sample outputs are correct; function signature matches samples; the advertised algorithm is necessary; the solution is unique and unambiguous. If any check fails, regenerate the question before returning it.

FUNCTION SIGNATURE FORMAT (CRITICAL — LANGUAGE-NEUTRAL ONLY)
function_signature must describe the function abstractly, NOT in any specific programming language.
parameter_types must use language-neutral type names: int, float, str, bool, list[int], list[str], etc.
FORBIDDEN: JavaScript syntax, "function" keyword, braces {{}}, semicolons, language-specific types.

Return EXACTLY 1 problem as a JSON ARRAY with one element. Return STRICT JSON ONLY.
Schema:
[
  {{
    "title": "",
    "description": "",
    "difficulty": "{next_difficulty}",
    "stage": "",
    "function_name": "",
    "function_signature": "",
    "return_type": "",
    "parameter_types": [],
    "constraints": [],
    "examples": [
      {{
        "input": "nums=[2,3,1,1,4]",
        "output": "2",
        "explanation": "..."
      }}
    ],
    "visible_testcases": [
      {{
        "input": {{
          "nums": [2, 3, 1, 1, 4]
        }},
        "output": 2
      }}
    ],
    "hidden_testcases": [
      {{
        "input": {{
          "nums": [10, 20, 30]
        }},
        "output": 3
      }}
    ]
  }}
]

Return STRICT JSON ONLY.
No markdown.
No explanations.
No comments.
No surrounding text.
No code fences.
"""