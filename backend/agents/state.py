"""
LangGraph State Definition for CodeForge.
"""

from typing import TypedDict, Optional, List

from schemas.submissions import (
    SkillProfile,
    AnalysisResult,
    WeaknessResult,
    TeachingMaterial,
    RemediationProblem,
    SkillUpdateResult,
    Roadmap,
    RoadmapDecision,
)


class MentorState(TypedDict):
    """
    Shared state flowing through the mentor graph.
    """

    # =====================================================
    # Input
    # =====================================================

    user_id: str
    problem_id: str

    submission_code: str
    submission_language: str

    is_remediation: bool

    # =====================================================
    # Loaded Context
    # =====================================================

    problem: Optional[dict]

    skill_profile: Optional[SkillProfile]

    roadmap: Optional[Roadmap]

    # =====================================================
    # Execution Results
    # =====================================================

    correct: Optional[bool]

    test_results: Optional[dict]

    # =====================================================
    # Analysis Node
    # =====================================================

    analysis: Optional[AnalysisResult]

    # =====================================================
    # Weakness Node
    # =====================================================

    weakness: Optional[WeaknessResult]

    # =====================================================
    # Teaching Node
    # =====================================================

    teaching_material: Optional[TeachingMaterial]

    # =====================================================
    # Remediation Node
    # =====================================================

    remediation_problems: Optional[
        List[RemediationProblem]
    ]

    # =====================================================
    # Skill Update Node
    # =====================================================

    skill_update: Optional[
        SkillUpdateResult
    ]

    # =====================================================
    # Roadmap Agent
    # =====================================================

    next_action: Optional[
        RoadmapDecision
    ]

    # =====================================================
    # Metadata
    # =====================================================

    submission_id: Optional[str]

    # =====================================================
    # Phase 2 – AI Practice
    # =====================================================

    ai_practice_problem: Optional[RemediationProblem]