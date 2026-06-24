from pydantic import BaseModel, model_serializer
from typing import Optional, List, Dict, Any, Literal

class Example(BaseModel):
    input: str
    output: str
    explanation: str


class TestCase(BaseModel):
    input: Dict[str, Any]
    output: Any
class ProblemCreate(BaseModel):

    title: str

    topic: str
    subtopic: str

    difficulty: Literal[
        "Easy",
        "Medium",
        "Hard"
    ]

    description: str

    function_name: str

    function_signature: str

    return_type: str

    parameter_types: List[str]

    constraints: List[str]

    expected_pattern: str

    expected_time_complexity: str
    expected_space_complexity: str

    examples: List[Example]

    visible_testcases: List[TestCase]
    hidden_testcases: List[TestCase]

    user_id: Optional[str] = None

class ProblemResponse(BaseModel):
    id: str
    title: str
    topic: str
    subtopic: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    description: str
    function_name: str
    function_signature: str
    return_type: str
    parameter_types: List[str]
    constraints: List[str]
    expected_pattern: str
    expected_time_complexity: str
    expected_space_complexity: str
    examples: List[Example]
    visible_testcases: List[TestCase]
    hidden_testcases: Optional[List[TestCase]] = None
    user_id: Optional[str] = None

    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        result = handler(self)
        result["_id"] = self.id
        return result