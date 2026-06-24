"""
Roadmap Service for CodeForge.

Manages user learning roadmaps, skill profiles, and progression
through the adaptive curriculum.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from bson import ObjectId

from schemas.submissions import (
    SkillProfile,
    SkillUpdateResult,
    SkillStats,
    Roadmap,
    RoadmapDecision
)

from database import (
    skill_profiles_collection,
    roadmaps_collection,
    problems_collection,
    generated_problems_collection,
)


async def get_or_create_skill_profile(user_id: str) -> SkillProfile:
    """Fetch the user's skill profile, creating a blank one if none exists."""
    profile = await skill_profiles_collection.find_one({"user_id": user_id})
    if profile:
        profile["id"] = str(profile["_id"])
        # Ensure stats has default dict keys if it is a raw dict
        if "stats" not in profile:
            profile["stats"] = SkillStats().model_dump()
        return SkillProfile(**profile)

    now = datetime.now(timezone.utc)

    new_profile = {
        "user_id": user_id,
        "mastery_scores": {},
        "stats": SkillStats().model_dump(),
        "created_at": now,
        "updated_at": now
    }
    result = await skill_profiles_collection.insert_one(new_profile)
    new_profile["id"] = str(result.inserted_id)
    return SkillProfile(**new_profile)


async def get_or_create_roadmap(user_id: str) -> Roadmap:
    """Fetch the user's roadmap, creating a default one if none exists."""
    roadmap = await roadmaps_collection.find_one({"user_id": user_id})
    if roadmap:
        roadmap["id"] = str(roadmap["_id"])
        return Roadmap(**roadmap)

    new_roadmap = {
        "user_id": user_id,
        "current_topic": None,
        "current_subtopic": None,
        "completed_topics": [],
        "completed_subtopics": [],
        "remediation_queue": [],
        "difficulty": "Easy",
        "active_remediation": None,
        "completed_problem_ids": [],
        "mode": "normal",
        "active_problem_id": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    result = await roadmaps_collection.insert_one(new_roadmap)
    new_roadmap["id"] = str(result.inserted_id)
    return Roadmap(**new_roadmap)


async def update_skill_score(
    user_id: str,
    topic: str,
    subtopic: str,
    delta: int,
) -> SkillUpdateResult:
    profile = await get_or_create_skill_profile(user_id)
    scores = profile.mastery_scores

    scores.setdefault(topic, {})
    scores[topic].setdefault(subtopic, 0)

    current = scores[topic][subtopic]
    new_score = max(0, min(100, current + delta))
    scores[topic][subtopic] = new_score

    await skill_profiles_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "mastery_scores": scores,
                "updated_at": datetime.now(timezone.utc),
            }
        }
    )

    return SkillUpdateResult(
        topic=topic,
        subtopic=subtopic,
        previous_score=current,
        new_score=new_score,
        delta=delta,
    )


async def add_remediation_to_roadmap(
    user_id: str,
    problem_ids: List[str],
) -> None:
    roadmap = await get_or_create_roadmap(user_id)
    queue = roadmap.remediation_queue
    
    for pid in problem_ids:
        if pid not in queue:
            queue.append(pid)

    await roadmaps_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "remediation_queue": queue,
                "active_remediation": queue[0] if queue else None,
                "mode": "remediation",
                "updated_at": datetime.now(timezone.utc),
            }
        }
    )


async def advance_roadmap(user_id: str, problem_id: str, correct: bool) -> None:
    """Advance the roadmap state based on submission correctness."""
    roadmap = await get_or_create_roadmap(user_id)
    profile = await get_or_create_skill_profile(user_id)

    # Update stats
    stats = profile.stats
    if correct:
        stats.problems_solved += 1
        if problem_id not in roadmap.completed_problem_ids:
            roadmap.completed_problem_ids.append(problem_id)
        
        # Check if solved problem is in the remediation queue
        if problem_id in roadmap.remediation_queue:
            roadmap.remediation_queue.remove(problem_id)
            stats.remediation_completed += 1
            
        # Update active remediation
        roadmap.active_remediation = roadmap.remediation_queue[0] if roadmap.remediation_queue else None
        if not roadmap.remediation_queue:
            roadmap.mode = "normal"
    else:
        stats.problems_failed += 1

    await skill_profiles_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "stats": stats.model_dump(),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    await roadmaps_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "completed_problem_ids": roadmap.completed_problem_ids,
                "remediation_queue": roadmap.remediation_queue,
                "active_remediation": roadmap.active_remediation,
                "mode": roadmap.mode,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )


async def recommend_next_problem(user_id: str) -> RoadmapDecision:
    """
    Priority-based recommendation:
    1. Active remediation problem
    2. Weakest skill (mastery < 70%): search generated first, then standard
    3. Continue current topic
    4. New topic / Fallback
    """
    roadmap = await get_or_create_roadmap(user_id)
    profile = await get_or_create_skill_profile(user_id)

    MASTERY_THRESHOLD = 70
    completed_ids = set(roadmap.completed_problem_ids)

    # 1. Active Remediation
    if roadmap.active_remediation:
        # Search in generated problems first
        problem = None
        try:
            problem = await generated_problems_collection.find_one({"_id": ObjectId(roadmap.active_remediation)})
        except Exception:
            pass
            
        if not problem:
            # Check standard problems just in case
            try:
                problem = await problems_collection.find_one({"_id": ObjectId(roadmap.active_remediation)})
            except Exception:
                pass

        if problem:
            return RoadmapDecision(
                action="remediation",
                next_topic=problem.get("topic"),
                next_subtopic=problem.get("subtopic"),
                next_problem_id=str(problem["_id"]),
                recommended_difficulty=roadmap.difficulty,
                reason="Please solve active remediation problem to unlock roadmap progress."
            )

    # 2. Find Weakest Skill < 70%
    mastery_scores = profile.mastery_scores
    weakest_topic = None
    weakest_subtopic = None
    lowest_score = 101

    for topic, subtopics in mastery_scores.items():
        for subtopic, score in subtopics.items():
            if score < lowest_score:
                lowest_score = score
                weakest_topic = topic
                weakest_subtopic = subtopic

    if weakest_topic and weakest_subtopic and lowest_score < MASTERY_THRESHOLD:
        # Check generated remediation problems first
        gen_prob = await generated_problems_collection.find_one({
            "user_id": user_id,
            "subtopic": weakest_subtopic
        })
        if gen_prob:
            # Set as active remediation
            pid = str(gen_prob["_id"])
            await roadmaps_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "active_remediation": pid,
                        "mode": "remediation",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return RoadmapDecision(
                action="remediation",
                next_topic=weakest_topic,
                next_subtopic=weakest_subtopic,
                next_problem_id=pid,
                recommended_difficulty=roadmap.difficulty,
                reason=f"Remediation generated for weak skill '{weakest_subtopic}' (score: {lowest_score}%)."
            )

        # Check standard problems in that weak subtopic
        db_query = {
            "topic": weakest_topic,
            "subtopic": weakest_subtopic,
            "difficulty": roadmap.difficulty
        }
        # Filter completed
        uncompleted_probs = []
        async for p in problems_collection.find(db_query):
            if str(p["_id"]) not in completed_ids:
                uncompleted_probs.append(p)
                
        if uncompleted_probs:
            target_prob = uncompleted_probs[0]
            pid = str(target_prob["_id"])
            await roadmaps_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "current_topic": weakest_topic,
                        "current_subtopic": weakest_subtopic,
                        "active_problem_id": pid,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return RoadmapDecision(
                action="recommend",
                next_topic=weakest_topic,
                next_subtopic=weakest_subtopic,
                next_problem_id=pid,
                recommended_difficulty=roadmap.difficulty,
                reason=f"Recommended practice problem for weak skill '{weakest_subtopic}' (score: {lowest_score}%)."
            )

    # 3. Continue Current Topic
    if roadmap.current_topic:
        uncompleted_in_topic = []
        async for p in problems_collection.find({"topic": roadmap.current_topic, "difficulty": roadmap.difficulty}):
            if str(p["_id"]) not in completed_ids:
                uncompleted_in_topic.append(p)
                
        if uncompleted_in_topic:
            target_prob = uncompleted_in_topic[0]
            pid = str(target_prob["_id"])
            await roadmaps_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "current_subtopic": target_prob.get("subtopic"),
                        "active_problem_id": pid,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return RoadmapDecision(
                action="continue",
                next_topic=roadmap.current_topic,
                next_subtopic=target_prob.get("subtopic"),
                next_problem_id=pid,
                recommended_difficulty=roadmap.difficulty,
                reason=f"Continue solving problems in your current topic '{roadmap.current_topic}'."
            )

    # 4. New Topic Recommendation
    # Find any uncompleted problems in any topic
    all_uncompleted = []
    async for p in problems_collection.find({"difficulty": roadmap.difficulty}):
        if str(p["_id"]) not in completed_ids:
            all_uncompleted.append(p)
            
    if all_uncompleted:
        target_prob = all_uncompleted[0]
        pid = str(target_prob["_id"])
        await roadmaps_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "current_topic": target_prob.get("topic"),
                    "current_subtopic": target_prob.get("subtopic"),
                    "active_problem_id": pid,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return RoadmapDecision(
            action="recommend",
            next_topic=target_prob.get("topic"),
            next_subtopic=target_prob.get("subtopic"),
            next_problem_id=pid,
            recommended_difficulty=roadmap.difficulty,
            reason=f"Recommended new topic: '{target_prob.get('topic')}'."
        )

    # 5. Fallback - Starter/Any Easy problem
    starter_problem = await problems_collection.find_one({"difficulty": "Easy"})
    if starter_problem:
        pid = str(starter_problem["_id"])
        return RoadmapDecision(
            action="recommend",
            next_topic=starter_problem.get("topic"),
            next_subtopic=starter_problem.get("subtopic"),
            next_problem_id=pid,
            recommended_difficulty="Easy",
            reason="All current difficulty problems completed! Starter problem recommended."
        )

    return RoadmapDecision(
        action="recommend",
        reason="No problems found in database."
    )
