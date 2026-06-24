import streamlit as st
import requests
import json

BASE_URL = "http://localhost:8000"

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]

problem = st.session_state.get("selected_problem")

if not problem:
    st.error("No problem selected")
    st.stop()

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

code = st.text_area(
    "Write your code here",
    height=350,
    placeholder="def solve():\n    pass"
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
                response = requests.post(
                    f"{BASE_URL}/submissions/",
                    json={
                        "problem_id": problem.get("_id", ""),
                        "code": code,
                        "language": "python"
                    },
                    headers={"Authorization": f"Bearer {token}"}
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

                    # ── Analysis ────────────────────────────────────
                    analysis = result.get("analysis", {})
                    if analysis:
                        st.subheader("📊 Code Analysis")
                        acol1, acol2, acol3, acol4 = st.columns(4)
                        with acol1:
                            st.metric("Time", analysis.get("time_complexity", "?"))
                        with acol2:
                            st.metric("Space", analysis.get("space_complexity", "?"))
                        with acol3:
                            st.metric("Your Pattern", analysis.get("pattern_used", "?"))
                        with acol4:
                            st.metric("Expected", analysis.get("pattern_expected", "?"))

                    # ── Weakness Detection ──────────────────────────
                    weakness = result.get("weakness", {})
                    if weakness and weakness.get("weakness_detected"):
                        st.divider()
                        st.subheader("⚠️ Weakness Detected")
                        st.warning(f"**{weakness.get('weakness', 'Unknown')}**: {weakness.get('reason', '')}")

                        # ── Teaching Material ──────────────────────
                        teaching = result.get("teaching")
                        if teaching:
                            st.divider()
                            st.subheader("📖 Let's Learn: " + teaching.get("concept", ""))
                            st.markdown(teaching.get("explanation", ""))

                            if teaching.get("example"):
                                st.subheader("💡 Example")
                                st.code(teaching.get("example", ""), language="python")

                            takeaways = teaching.get("key_takeaways", [])
                            if takeaways:
                                st.subheader("🎯 Key Takeaways")
                                for t in takeaways:
                                    st.markdown(f"- {t}")

                        # ── Remediation Problems ───────────────────
                        remediation = result.get("remediation_problems", [])
                        if remediation:
                            st.divider()
                            st.subheader("🏋️ Practice Problems")
                            st.info("Complete these practice problems before continuing the roadmap.")

                            for ridx, rprob in enumerate(remediation, start=1):
                                with st.expander(f"Practice {ridx}: {rprob.get('title', 'Problem')}", expanded=(ridx == 1)):
                                    st.markdown(f"**Difficulty:** {rprob.get('difficulty', 'Unknown')}")
                                    st.markdown(rprob.get("description", ""))
                                    if rprob.get("_id"):
                                        if st.button(f"Solve Practice {ridx} 🚀", key=f"remediation_{ridx}"):
                                            st.session_state["selected_problem"] = rprob
                                            st.rerun()

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
                            next_action = result.get("next_action", "continue")
                            action_labels = {
                                "continue": "➡️ Next Problem",
                                "remediation": "📝 Practice First",
                                "topic_complete": "🎉 Topic Complete!",
                                "advance": "🆙 Next Topic!",
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