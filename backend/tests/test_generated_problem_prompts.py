import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.prompts import build_ai_practice_prompt, build_remediation_prompt
from agents.mentor_nodes import should_teach


def test_ai_practice_prompt_requires_interview_quality_and_validation():
    prompt = build_ai_practice_prompt(
        problem={"title": "Two Sum", "topic": "Arrays", "subtopic": "Hashing"},
        mastery=70,
        history={"titles": [], "completed": [], "descriptions": [], "patterns": []},
        current_difficulty="Medium",
    )

    lowered = prompt.lower()
    assert "interview" in lowered
    assert "internally consistent" in lowered
    assert "sample" in lowered
    assert "expected algorithm" in lowered or "expected output" in lowered
    assert "exactly one" in lowered
    assert "unambiguous interpretation" in lowered
    assert "at least 2 sample" in lowered or "2 sample" in lowered
    assert "internal verify" in lowered or "internally verify" in lowered
    assert "algorithm" in lowered and "required" in lowered


def test_remediation_prompt_requires_realistic_constraints_and_examples():
    prompt = build_remediation_prompt(
        problem={"title": "Two Sum", "topic": "Arrays", "subtopic": "Hashing"},
        weakness="hashing",
        mastery=40,
        history={"titles": [], "completed": [], "descriptions": [], "patterns": []},
        num_problems=1,
    )

    lowered = prompt.lower()
    assert "meaningful title" in lowered
    assert "correct constraints" in lowered
    assert "valid sample test cases" in lowered
    assert "expected algorithm" in lowered
    assert "time complexity" in lowered
    assert "exactly one unambiguous interpretation" in lowered or "one unambiguous interpretation" in lowered
    assert "every variable" in lowered and "function signature" in lowered
    assert "every sample output" in lowered and "derivable" in lowered
    assert "hidden test cases" in lowered


def test_should_teach_routes_incorrect_submission_to_remediation():
    state = {
        "analysis": SimpleNamespace(correct=False),
        "weakness": None,
    }

    assert should_teach(state) == "remediation"
