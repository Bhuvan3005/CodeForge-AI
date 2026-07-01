"""
Roadmap Service

Handles

- Skill Profiles
- Learning Roadmap
- Adaptive Recommendations
- Progress Tracking
"""

from datetime import datetime, timezone
from typing import Dict, List
from bson import ObjectId

from schemas.submissions import (
    SkillProfile,
    SkillUpdateResult,
    SkillStats,
    Roadmap,
    RoadmapDecision,
)

from database import (
    skill_profiles_collection,
    roadmaps_collection,
    problems_collection,
    generated_problems_collection,
)

TOPIC_ORDER = [

    "Arrays",

    "Two Pointers",

    "Sliding Window",

    "Binary Search",

    "Stack",

    "Queue",

    "Linked List",

    "Trees",

    "Graphs",

    "Heap",

    "Greedy",

    "Backtracking",

    "Dynamic Programming",
]

MASTERY_THRESHOLD = 70

MAX_SCORE = 100

MIN_SCORE = 0


    
def clamp_score(score: int) -> int:
    """
    Keep mastery score between
    0 and 100.
    """

    return max(
        MIN_SCORE,
        min(MAX_SCORE, score),
    )
    
def difficulty_for_mastery(
    mastery: float,
) -> str:
    """
    Decide roadmap difficulty from
    average mastery.
    """

    if mastery < 40:
        return "Easy"

    if mastery < 75:
        return "Medium"

    return "Hard"

def next_topic(
    current: str | None,
) -> str | None:
    """
    Return the next curriculum topic.
    """

    if current is None:
        return TOPIC_ORDER[0]

    if current not in TOPIC_ORDER:
        return TOPIC_ORDER[0]

    index = TOPIC_ORDER.index(
        current
    )

    if index == len(TOPIC_ORDER) - 1:
        return None

    return TOPIC_ORDER[index + 1]

async def get_or_create_skill_profile(
    user_id: str,
) -> SkillProfile:
    """
    Fetch existing profile or
    create a new one.
    """

    profile = await skill_profiles_collection.find_one(
        {
            "user_id": user_id
        }
    )

    if profile:

        profile.pop("_id", None)

        profile.setdefault(
            "stats",
            SkillStats().model_dump(),
        )

        return SkillProfile(
            **profile
        )

    now = datetime.now(
        timezone.utc
    )

    document = {

        "user_id": user_id,

        "mastery_scores": {},

        "stats": SkillStats().model_dump(),

        "created_at": now,

        "updated_at": now,
    }

    await skill_profiles_collection.insert_one(
        document
    )

    return SkillProfile(
        **document
    )
    
async def get_or_create_roadmap(
    user_id: str,
) -> Roadmap:
    """
    Fetch user's roadmap or create
    a fresh roadmap.
    """

    roadmap = await roadmaps_collection.find_one(
        {
            "user_id": user_id
        }
    )

    if roadmap:

        roadmap.pop(
            "_id",
            None,
        )

        return Roadmap(
            **roadmap
        )

    now = datetime.now(
        timezone.utc
    )

    roadmap = {

        "user_id": user_id,

        "current_topic": None,

        "current_subtopic": None,

        "completed_topics": [],

        "completed_subtopics": [],

        "completed_problem_ids": [],

        "difficulty": "Easy",

        "mode": "normal",

        "active_problem_id": None,

        "active_remediation": None,

        "remediation_queue": [],

        "created_at": now,

        "updated_at": now,
    }

    await roadmaps_collection.insert_one(
        roadmap
    )

    return Roadmap(
        **roadmap
    )
    
async def add_remediation_to_roadmap(
    user_id: str,
    problem_ids: List[str],
) -> None:
    """
    Add generated remediation problems to
    the user's remediation queue.
    """

    roadmap = await get_or_create_roadmap(
        user_id
    )

    queue = roadmap.remediation_queue.copy()

    for pid in problem_ids:

        if pid not in queue:
            queue.append(pid)

    await roadmaps_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$set": {

                "mode": "remediation",

                "remediation_queue": queue,

                "active_remediation": (
                    queue[0]
                    if queue
                    else None
                ),

                "updated_at": datetime.now(
                    timezone.utc
                ),
            }
        }
    )
async def advance_roadmap(
    user_id: str,
    problem_id: str,
    correct: bool,
) -> None:
    """
    Update roadmap after every submission.
    """

    roadmap = await get_or_create_roadmap(
        user_id
    )

    profile = await get_or_create_skill_profile(
        user_id
    )

    stats = profile.stats

    completed = roadmap.completed_problem_ids.copy()

    queue = roadmap.remediation_queue.copy()

    ####################################################
    # Correct Submission
    ####################################################

    if correct:

        stats.problems_solved += 1

        if problem_id not in completed:
            completed.append(problem_id)

        if problem_id in queue:

            queue.remove(problem_id)

            stats.remediation_completed += 1

        active = (
            queue[0]
            if queue
            else None
        )

        mode = (
            "remediation"
            if queue
            else "normal"
        )

    ####################################################
    # Failed Submission
    ####################################################

    else:

        stats.problems_failed += 1

        active = roadmap.active_remediation

        mode = roadmap.mode

    ####################################################
    # Difficulty Progression
    ####################################################

    avg = average_mastery(
        profile
    )

    difficulty = difficulty_for_mastery(
        avg
    )

    ####################################################
    # Update Skill Profile
    ####################################################

    await skill_profiles_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$set": {

                "stats": stats.model_dump(),

                "updated_at": datetime.now(
                    timezone.utc
                ),
            }
        }
    )

    ####################################################
    # Update Roadmap
    ####################################################

    await roadmaps_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$set": {

                "completed_problem_ids":
                    completed,

                "remediation_queue":
                    queue,

                "active_remediation":
                    active,

                "difficulty":
                    difficulty,

                "mode":
                    mode,

                "updated_at":
                    datetime.now(
                        timezone.utc
                    ),
            }
        }
    )



async def recommend_next_problem(
    user_id: str,
) -> RoadmapDecision:
    """
    Recommendation Priority

    1. Active remediation
    2. Continue current topic
    3. Weakest skill
    4. Next curriculum topic
    5. Any remaining problem
    """

    roadmap = await get_or_create_roadmap(
        user_id
    )

    profile = await get_or_create_skill_profile(
        user_id
    )

    completed = set(
        roadmap.completed_problem_ids
    )

    ##################################################
    # 1. Active Remediation
    ##################################################

    if roadmap.active_remediation:

        try:

            problem = await generated_problems_collection.find_one(
                {
                    "_id": ObjectId(
                        roadmap.active_remediation
                    )
                }
            )

            if problem:

                return RoadmapDecision(

                    action="remediation",

                    next_topic=problem["topic"],

                    next_subtopic=problem["subtopic"],

                    next_problem_id=str(
                        problem["_id"]
                    ),

                    recommended_difficulty=roadmap.difficulty,

                    reason="Complete your remediation before continuing."
                )

        except Exception:
            pass

    ##################################################
    # 2. Continue Current Topic
    ##################################################

    if roadmap.current_topic:

        async for problem in problems_collection.find(

            {

                "topic": roadmap.current_topic,

                "difficulty": roadmap.difficulty,

            }

        ):

            if str(problem["_id"]) in completed:
                continue

            pid = str(problem["_id"])

            await roadmaps_collection.update_one(

                {
                    "user_id": user_id
                },

                {
                    "$set": {

                        "current_subtopic":
                            problem["subtopic"],

                        "active_problem_id":
                            pid,

                        "updated_at":
                            datetime.now(
                                timezone.utc
                            ),
                    }
                }
            )

            return RoadmapDecision(

                action="continue",

                next_topic=problem["topic"],

                next_subtopic=problem["subtopic"],

                next_problem_id=pid,

                recommended_difficulty=roadmap.difficulty,

                reason="Continue your current learning path."
            )

    ##################################################
    # 3. Weakest Skill
    ##################################################

    weakest_topic = None
    weakest_subtopic = None
    lowest = 101

    for topic, subtopics in profile.mastery_scores.items():

        for subtopic, score in subtopics.items():

            if score < lowest:

                lowest = score

                weakest_topic = topic

                weakest_subtopic = subtopic

    if (

        weakest_topic

        and

        lowest < MASTERY_THRESHOLD

    ):

        async for problem in problems_collection.find(

            {

                "topic": weakest_topic,

                "subtopic": weakest_subtopic,

                "difficulty": roadmap.difficulty,

            }

        ):

            if str(problem["_id"]) in completed:
                continue

            pid = str(problem["_id"])

            await roadmaps_collection.update_one(

                {

                    "user_id": user_id

                },

                {

                    "$set": {

                        "current_topic":
                            weakest_topic,

                        "current_subtopic":
                            weakest_subtopic,

                        "active_problem_id":
                            pid,

                        "updated_at":
                            datetime.now(
                                timezone.utc
                            ),
                    }

                }

            )

            return RoadmapDecision(

                action="recommend",

                next_topic=weakest_topic,

                next_subtopic=weakest_subtopic,

                next_problem_id=pid,

                recommended_difficulty=roadmap.difficulty,

                reason=(
                    f"Strengthen {weakest_subtopic} "
                    f"(Mastery {lowest}%)."
                ),
            )

    ##################################################
    # 4. Curriculum Progression
    ##################################################

    topic = next_topic(
        roadmap.current_topic
    )

    while topic:

        async for problem in problems_collection.find(

            {

                "topic": topic,

                "difficulty": roadmap.difficulty,

            }

        ):

            if str(problem["_id"]) in completed:
                continue

            pid = str(problem["_id"])

            await roadmaps_collection.update_one(

                {

                    "user_id": user_id

                },

                {

                    "$set": {

                        "current_topic": topic,

                        "current_subtopic":
                            problem["subtopic"],

                        "active_problem_id":
                            pid,

                        "updated_at":
                            datetime.now(
                                timezone.utc
                            ),
                    }

                }

            )

            return RoadmapDecision(

                action="recommend",

                next_topic=topic,

                next_subtopic=problem["subtopic"],

                next_problem_id=pid,

                recommended_difficulty=roadmap.difficulty,

                reason=f"Start learning {topic}.",
            )

        topic = next_topic(
            topic
        )

    ##################################################
    # 5. Any Remaining Problem
    ##################################################

    async for problem in problems_collection.find(

        {

            "difficulty":
                roadmap.difficulty

        }

    ):

        if str(problem["_id"]) in completed:
            continue

        return RoadmapDecision(

            action="recommend",

            next_topic=problem["topic"],

            next_subtopic=problem["subtopic"],

            next_problem_id=str(
                problem["_id"]
            ),

            recommended_difficulty=roadmap.difficulty,

            reason="Recommended remaining problem.",
        )

    ##################################################
    # Finished
    ##################################################

    return RoadmapDecision(

        action="complete",

        reason=(
            "Congratulations! "
            "You have completed all available problems."
        ),
    )
    
async def update_skill_score(
    user_id: str,
    topic: str,
    subtopic: str,
    delta: int,
    solved: bool,
    remediation: bool = False,
):
    """
    Update mastery score and user statistics.
    """

    profile = await get_or_create_skill_profile(user_id)

    profile.mastery_scores.setdefault(topic, {})
    profile.mastery_scores[topic].setdefault(subtopic, 0)

    current = profile.mastery_scores[topic][subtopic]

    new_score = clamp_score(current + delta)

    profile.mastery_scores[topic][subtopic] = new_score

    if solved:
        profile.stats.problems_solved += 1
    else:
        profile.stats.problems_failed += 1

    if remediation and solved:
        profile.stats.remediation_completed += 1

    await skill_profiles_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "mastery_scores": profile.mastery_scores,
                "stats": profile.stats.model_dump(),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return profile

def average_mastery(profile: SkillProfile) -> float:
    scores = []

    for topic in profile.mastery_scores.values():
        scores.extend(topic.values())

    if not scores:
        return 0

    return sum(scores) / len(scores)