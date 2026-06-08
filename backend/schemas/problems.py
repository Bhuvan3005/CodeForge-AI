from pydantic import BaseModel
from typing import Optional, List, Dict, Any


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
    difficulty: str

    description: str

    examples: List[Example]

    visible_testcases: List[TestCase]
    hidden_testcases: List[TestCase]

    # None => public problem
    # user_id => user-specific problem
    user_id: Optional[str] = None
    
    

class ProblemResponse(BaseModel):
    id: Optional[str]=None

    title: str
    topic: str
    difficulty: str

    description: str

    examples: List[Example]

    visible_testcases: List[TestCase]

    # hidden testcases should usually not be returned
    user_id: Optional[str] = None