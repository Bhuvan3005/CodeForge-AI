from pydantic import BaseModel


class ProgressCreate(BaseModel):
    level: int = 1
    xp: int = 0
    problems_solved: int = 0


class ProgressResponse(BaseModel):
    level: int
    xp: int
    problems_solved: int