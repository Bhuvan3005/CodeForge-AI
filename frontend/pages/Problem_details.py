import streamlit as st
import requests
import json

BASE_URL = "http://localhost:8000"


def get_problem_id(problem: dict) -> str:
    """Resolve the canonical string id from API or session problem payloads."""
    return (
        problem.get("id")
        or problem.get("problem_id")
        or problem.get("_id")
        or ""
    )

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]


def load_problem_from_state() -> dict | None:
    active_problem_id = (
        st.session_state.get("problem_id")
        or st.session_state.get("generated_problem_id")
        or st.session_state.get("current_problem_id")
        or ""
    )
    problem = st.session_state.get("selected_problem")

    if problem and active_problem_id and get_problem_id(problem) == active_problem_id:
        return problem

    if active_problem_id:
        print("Loaded Problem ID:", active_problem_id)
        try:
            response = requests.get(
                f"{BASE_URL}/problems/id/{active_problem_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 200:
                loaded_problem = response.json()
                st.session_state["selected_problem"] = loaded_problem
                st.session_state["current_problem"] = loaded_problem
                st.session_state["problem_id"] = active_problem_id
                st.session_state["current_problem_id"] = active_problem_id
                return loaded_problem
        except Exception as exc:
            print("Failed to reload problem", exc)

    return problem


problem = load_problem_from_state()

if not problem:
    st.error("No problem selected")
    st.stop()

# Phase 1 – Informational banner for difficult problems (never blocks access)
banner_info = st.session_state.get("difficulty_banner", {})
if banner_info.get("show"):
    prereq = banner_info.get("prereq")
    if prereq:
        st.info(
            f"⚠️ **This problem may be challenging based on your current progress.**\n\n"
            f"Recommended prerequisite: **{prereq}**\n\n"
            f"You can still attempt this problem."
        )
    else:
        st.info(
            "⚠️ **This problem may be challenging based on your current progress.**\n\n"
            "You can still attempt this problem."
        )

# Header
st.title(problem.get("title", "Untitled Problem"))

col1, col2 = st.columns(2)

with col1:
    difficulty = problem.get("difficulty", "Unknown")

    difficulty_color = {
        "Easy": "🟢 Easy",
        "Medium": "🟡 Medium",
        "Hard": "🔴 Hard"
    }

    st.markdown(
        f"### {difficulty_color.get(difficulty, difficulty)}"
    )

with col2:
    topic = problem.get("topic", "General")
    st.markdown(f"### 📚 {topic}")

st.divider()

# Description
st.subheader("📝 Problem Description")
st.write(problem.get("description", "No description available."))

# Constraints
constraints = problem.get("constraints")

if constraints:
    st.subheader("📌 Constraints")

    if isinstance(constraints, list):
        for c in constraints:
            st.markdown(f"- {c}")
    else:
        st.write(constraints)

# Test Cases
testcases = problem.get("visible_testcases", [])

if testcases:
    st.subheader("🧪 Sample Test Cases")

    for idx, testcase in enumerate(testcases, start=1):
        with st.expander(f"Test Case {idx}", expanded=(idx == 1)):
            st.code(
                f"""Input:
{testcase.get('input', '')}

Output:
{testcase.get('output', '')}
""",
                language="text"
            )

st.divider()

# Code Editor
st.subheader("💻 Your Solution")

language = st.selectbox(
    "Programming Language",
    ["Python", "C++"],
    index=0,
)

placeholders = {
    "Python": """def solve():
    pass""",

    "C++": """#include <vector>
using namespace std;

int solve() {

}
""",
}

code = st.text_area(
    f"Write your {language} solution",
    height=350,
    placeholder=placeholders[language],
)

col1, col2 = st.columns([1, 5])

with col1:
    submit = st.button("🚀 Submit", use_container_width=True)
    

with col2:
    if st.button("⬅ Back", use_container_width=True):
        st.switch_page("pages/Topic_detail.py")


# ── Handle Submission ───────────────────────────────────────────────
if submit:
    if not code.strip():
        st.error("Please write your solution before submitting.")
    else:
        with st.spinner("🔄 Analyzing your submission..."):
            try:
                language_map = {
                "Python": "python",
                "C++": "cpp",
                }

                response = requests.post(
                    f"{BASE_URL}/submissions/",
                    json={
                        "problem_id": get_problem_id(problem),
                        "code": code,
                        "language": language_map[language],
                    },
                    headers={
                        "Authorization": f"Bearer {token}"
                    },
                )

                if response.status_code == 200:
                    result = response.json()

                    # ── Test Results ────────────────────────────────
                    st.divider()
                    correct = result.get("correct", False)
                    tests_passed = result.get("tests_passed", 0)
                    tests_total = result.get("tests_total", 0)

                    if correct:
                        st.success(f"✅ All tests passed! ({tests_passed}/{tests_total})")
                    else:
                        st.error(f"❌ {tests_passed}/{tests_total} tests passed")

                    # ── Mentor Report ────────────────────────────────
                    st.divider()
                    st.markdown("## 🧑‍🏫 Mentor Report")

                    # 1. Complexity Analysis
                    analysis = result.get("analysis", {})
                    if analysis:
                        st.subheader("📊 Complexity Analysis")
                        acol1, acol2, acol3, acol4 = st.columns(4)
                        with acol1:
                            st.metric("Time", analysis.get("time_complexity", "?"))
                        with acol2:
                            st.metric("Space", analysis.get("space_complexity", "?"))
                        with acol3:
                            st.metric("Detected Pattern", analysis.get("pattern_used", "?"))
                        with acol4:
                            st.metric("Expected", analysis.get("pattern_expected", "?"))

                    # 2 & 3. Strengths and Weaknesses
                    strengths = analysis.get("strengths", []) if analysis else []
                    weaknesses_list = analysis.get("weaknesses", []) if analysis else []

                    st.divider()
                    sw_col1, sw_col2 = st.columns(2)

                    with sw_col1:
                        st.subheader("💪 Strengths")
                        if strengths:
                            for s in strengths:
                                st.markdown(f"✅ {s}")
                        else:
                            st.markdown("_No specific strengths identified._")

                    with sw_col2:
                        st.subheader("⚠️ Areas to Improve")
                        if weaknesses_list:
                            for w in weaknesses_list:
                                st.markdown(f"⚠ {w}")
                        else:
                            st.markdown("_No significant weaknesses detected._")

                    # 4. Problem Insights
                    teaching = result.get("teaching")
                    if teaching:
                        st.divider()
                        st.subheader("📖 Problem Insights")
                        st.markdown(f"**Concept: {teaching.get('concept', '')}**")
                        st.markdown(teaching.get("explanation", ""))

                        if teaching.get("example"):
                            st.subheader("💡 Example")
                            st.code(
                                teaching.get("example", ""),
                                language="python" if language == "Python" else "cpp",
                            )

                        takeaways = teaching.get("key_takeaways", [])
                        if takeaways:
                            st.subheader("🎯 Key Takeaways")
                            for t in takeaways:
                                st.markdown(f"- {t}")

                    # 5. AI Practice
                    st.divider()
                    st.subheader("🎯 AI Practice")
                    
                    # Look for AI practice from correct submission or remediation
                    ai_practice = None
                    ai_reason = ""
                    
                    if correct:
                        ai_practice = result.get("ai_practice_problem")
                        if ai_practice:
                            concept = ai_practice.get("expected_pattern") or ai_practice.get("weakness") or "the same concept"
                            ai_reason = ai_practice.get("reason") or f"You solved the current problem correctly. This challenge introduces one additional <b>{concept}</b> concept to deepen your mastery."
                    else:
                        ai_practice = result.get("ai_practice_problem")
                        if not ai_practice:
                            remediation = result.get("remediation_problems", [])
                            if remediation and len(remediation) > 0:
                                ai_practice = remediation[0]
                        if ai_practice:
                            concept = ai_practice.get("expected_pattern") or ai_practice.get("weakness") or "the missing concept"
                            ai_reason = ai_practice.get("reason") or f"This problem will help you practice <b>{concept}</b>."

                    if ai_practice:
                        ai_difficulty = ai_practice.get("difficulty", "Medium")
                        
                        st.markdown(
                            f"""
                            <div style="background: linear-gradient(135deg, #1a1f2e, #0d1117); border: 1px solid #7C3AED; border-radius: 12px; padding: 20px; margin-bottom: 16px;">
                                <div style="color: #A78BFA; font-size: 13px; font-weight: 700; margin-bottom: 6px;">🤖 ADAPTIVE AI PRACTICE</div>
                                <div style="font-size: 20px; font-weight: bold; color: #F1F5F9; margin-bottom: 6px;">{ai_practice.get('title', 'AI Challenge')}</div>
                                <div style="color: #64748B; font-size: 13px;">
                                    Difficulty: <b style="color: #A78BFA;">{ai_difficulty}</b>
                                </div>
                                <div style="color: #64748B; font-size: 13px; margin-top: 4px;">
                                    Reason: {ai_reason}
                                </div>
                                <div style="color: #64748B; font-size: 13px; margin-top: 8px;">
                                    {ai_practice.get('description', '')[:100]}...
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if st.button("Solve AI Practice 🚀", key="solve_ai_practice_direct"):
                            st.session_state.pop("difficulty_banner", None)
                            problem_id = get_problem_id(ai_practice)
                            print("Solve AI Practice clicked")
                            print("Generated Problem ID:", problem_id)
                            st.session_state["selected_problem"] = ai_practice
                            st.session_state["problem_id"] = problem_id
                            st.session_state["current_problem_id"] = problem_id
                            st.session_state["generated_problem_id"] = problem_id
                            st.session_state["current_problem"] = ai_practice
                            print("Updating session_state")
                            st.switch_page("pages/Problem_details.py")

                    # ── Skill Update ───────────────────────────────
                    skill_upd = result.get("skill_update")
                    if skill_upd:
                        st.divider()
                        st.subheader("📈 Skill Update")
                        scol1, scol2, scol3 = st.columns(3)
                        with scol1:
                            st.metric(
                                f"{skill_upd.get('subtopic', 'Skill')}",
                                f"{skill_upd.get('new_score', 0)}%",
                                delta=f"{skill_upd.get('delta', 0)}%"
                            )
                        with scol2:
                            st.metric("Topic", skill_upd.get("topic", ""))
                        with scol3:
                            next_action = result.get("roadmap", {}).get("action", "continue")
                            action_labels = {
                                "continue": "➡️ Next Problem",
                                "remediation": "📝 Practice First",
                                "topic_complete": "🎉 Topic Complete!",
                                "advance": "🆙 Next Topic!",
                                "recommend": "🎯 Recommended",
                            }
                            st.metric("Next Step", action_labels.get(next_action, next_action))

                else:
                    try:
                        detail = response.json().get("detail", "Submission failed")
                    except Exception:
                        detail = f"Error: {response.status_code}"
                    st.error(detail)

            except Exception as e:
                st.error(f"Connection error: {str(e)}")