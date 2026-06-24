from pydantic import BaseModel,Field, model_serializer
from typing import Optional, List, Dict, Any,Literal
from datetime import datetime
from .problems import Example,TestCase

class SkillStats(BaseModel):
    problems_solved: int = 0
    problems_failed: int = 0
    remediation_completed: int = 0


class SkillProfile(BaseModel):
    user_id: str

    mastery_scores: Dict[
        str,               # topic
        Dict[str, int]     # subtopic -> score
    ] = Field(default_factory=dict)

    stats: SkillStats = Field(
        default_factory=SkillStats
    )

    created_at: datetime
    updated_at: datetime
    
class SkillUpdateResult(BaseModel):
    topic: str
    subtopic: str
    previous_score: int
    new_score: int
    delta: int

class RoadmapDecision(BaseModel):

    action: Literal[
        "continue",
        "teach",
        "remediation",
        "recommend"
    ]

    next_topic: Optional[str] = None

    next_subtopic: Optional[str] = None

    next_problem_id: Optional[str] = None

    recommended_difficulty: Optional[
        Literal[
            "Easy",
            "Medium",
            "Hard"
        ]
    ] = None

    reason: Optional[str] = None
    
class Roadmap(BaseModel):
    user_id: str

    current_topic: Optional[str] = None
    current_subtopic: Optional[str] = None

    completed_topics: list[str] = Field(default_factory=list)

    completed_subtopics: list[str] = Field(default_factory=list)

    remediation_queue: list[str] = Field(default_factory=list)

    difficulty: Literal[
        "Easy",
        "Medium",
        "Hard"
    ] = "Easy"

    active_remediation: Optional[str] = None
    
    completed_problem_ids: List[str] = Field(
        default_factory=list)

    mode: Literal[
        "normal",
        "teaching",
        "remediation"
    ] = "normal"
    
    active_problem_id: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SubmissionCreate(BaseModel):
    """Schema for incoming code submissions from the frontend."""
    
    problem_id: str
    code: str

    language: Literal[
        "python",
        "cpp"
    ] = "cpp"



class AnalysisResult(BaseModel):
    """Output from Submission Analysis Node"""

    correct: bool
    tests_passed: int
    tests_total: int

    time_complexity: str
    expected_time_complexity: str

    space_complexity: str
    expected_space_complexity: str

    pattern_used: str
    pattern_expected: str

    topic: str
    subtopic: str

    optimization_possible: bool = False
    optimization_reason: Optional[str] = None



class WeaknessResult(BaseModel):
    weakness_detected: bool

    weakness: Optional[str] = None
    reason: Optional[str] = None

    severity: Optional[
        Literal["low", "medium", "high"]
    ] = None

    mastery_delta: int = 0

    action: Literal[
        "continue",
        "teach",
        "remediation",
        "recommend"
    ]="continue"
    
    
class TeachingMaterial(BaseModel):
    """Output from Teaching Node"""

    concept: str

    explanation: str

    why_it_matters: str

    example: str

    key_takeaways: List[str]

    common_mistakes: List[str]

    optimization_tip: str


class RemediationProblem(BaseModel):
    problem_id: str

    title: str

    topic: str
    subtopic: str

    difficulty: Literal[
        "Easy",
        "Medium",
        "Hard"
    ]

    description: str

    # NEW
    function_name: str

    # NEW
    function_signature: str

    constraints: List[str]

    expected_pattern: str

    expected_time_complexity: str
    expected_space_complexity: str

    examples: List[Example]

    visible_testcases: List[TestCase]

    hidden_testcases: List[TestCase]

    generated_for: str

    weakness: str

    user_id: str

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        result = handler(self)
        result["_id"] = self.problem_id
        return result




class SubmissionResponse(BaseModel):
    submission_id: str

    # Execution Results
    correct: bool
    tests_passed: int
    tests_total: int

    # Analysis Node
    analysis: AnalysisResult

    # Weakness Detection Node
    weakness: Optional[WeaknessResult] = None

    # Teaching Node
    teaching: Optional[TeachingMaterial] = None

    # Remediation Node
    remediation_problems: Optional[
        List[RemediationProblem]
    ] = None

    # Skill Update Node
    skill_profile: Optional[
        SkillProfile
    ] = None

    # Roadmap Agent
    roadmap: RoadmapDecision

class RemediationResponse(BaseModel):
    remediation_active: bool
    active_problem_id: Optional[str] = None
    problems: List[RemediationProblem]

class DashboardResponse(BaseModel):
    problems_solved: int
    problems_failed: int
    remediation_completed: int
    mastery_scores: Dict[str, Dict[str, int]]
    current_topic: Optional[str] = None
    current_subtopic: Optional[str] = None
    active_problem_id: Optional[str] = None
    active_remediation_id: Optional[str] = None