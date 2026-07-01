import streamlit as st
import requests

BASE_URL = "http://localhost:8000"


def get_problem_id(problem: dict) -> str:
    return (
        problem.get("id")
        or problem.get("problem_id")
        or problem.get("_id")
        or ""
    )


def navigate_to_problem(problem: dict) -> None:
    problem_id = get_problem_id(problem)
    print("Solve AI Practice clicked")
    print("Generated Problem ID:", problem_id)
    st.session_state["selected_problem"] = problem
    st.session_state["problem_id"] = problem_id
    st.session_state["current_problem_id"] = problem_id
    st.session_state["generated_problem_id"] = problem_id
    st.session_state["current_problem"] = problem
    print("Updating session_state")
    st.switch_page("pages/Problem_details.py")


st.set_page_config(page_title="CodeForge - Topic Details", page_icon="📚", layout="wide")

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]
topic = st.session_state.get("selected_topic")

if not topic:
    st.error("No topic selected")
    st.stop()

# Verify session
response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code != 200:
    st.error("Session expired")
    st.stop()

# Header layout
col_title, col_back = st.columns([6, 1])
with col_title:
    st.title(f"📚 {topic}")
with col_back:
    if st.button("⬅ Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

# Custom Styling
st.markdown("""
<style>
.problem-card {
    background: #0E1117;
    border: 1px solid #30363D;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s, border-color 0.2s;
}
.problem-card:hover {
    transform: translateY(-2px);
    border-color: #3B82F6;
}
.remediation-card {
    background: #1C1515;
    border: 1px solid #FF4B4B;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 4px 10px rgba(255, 75, 75, 0.15);
    transition: transform 0.2s, border-color 0.2s;
}
.remediation-card:hover {
    transform: translateY(-2px);
    border-color: #FF8F8F;
}
.ai-practice-card {
    background: linear-gradient(135deg, #1a1f2e, #0d1117);
    border: 1px solid #7C3AED;
    padding: 24px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 4px 20px rgba(124, 58, 237, 0.2);
    transition: transform 0.2s, border-color 0.2s;
}
.ai-practice-card:hover {
    transform: translateY(-2px);
    border-color: #A78BFA;
}
.problem-title {
    font-size: 22px;
    font-weight: bold;
}
.problem-difficulty {
    color: #8B949E;
    font-size: 14px;
    margin-top: 5px;
}
.badge-fixed {
    background: #1F6FEB;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
}
.badge-ai {
    background: #7C3AED;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
}
.badge-remediation {
    background: #FF4B4B;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
}
.info-banner {
    background: #1c2435;
    border: 1px solid #3B82F6;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #93C5FD;
}
.section-header {
    font-size: 20px;
    font-weight: 700;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #30363D;
}
</style>
""", unsafe_allow_html=True)

# ─── Fetch Data ───────────────────────────────────────────────────────────────

# Fetch roadmap to get completed problem IDs and active remediation
roadmap_resp = requests.get(
    f"{BASE_URL}/roadmap/status",
    headers={"Authorization": f"Bearer {token}"}
)
roadmap = roadmap_resp.json() if roadmap_resp.status_code == 200 else {}
completed_ids = set(roadmap.get("completed_problem_ids", []))
active_problem_id = roadmap.get("active_problem_id")

# Fetch remediation status (we show remediation problems separately but don't lock anything)
remediation_resp = requests.get(
    f"{BASE_URL}/roadmap/remediation",
    headers={"Authorization": f"Bearer {token}"}
)
remediation = remediation_resp.json() if remediation_resp.status_code == 200 else {}
remediation_problem_ids = set(
    p.get("problem_id", p.get("id", "")) for p in remediation.get("problems", [])
)

# Fetch all problems for this topic
response = requests.get(
    f"{BASE_URL}/problems/{topic}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code != 200:
    st.error("Failed to fetch problems")
    st.stop()

problems = response.json()

# Fetch AI practice history for this topic (newest first)
ai_practice_resp = requests.get(
    f"{BASE_URL}/roadmap/ai-practice/{topic}",
    headers={"Authorization": f"Bearer {token}"}
)
ai_practice_history = ai_practice_resp.json() if ai_practice_resp.status_code == 200 else []
if not isinstance(ai_practice_history, list):
    ai_practice_history = []
ai_practice = ai_practice_history[0] if ai_practice_history else None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_problem_status(problem: dict) -> tuple[str, str]:
    """
    Phase 1 – Return (status_emoji, status_label) without ever locking.
    Priority: Completed > Recommended (active) > Remediation > Stretch/Advanced > Not Started
    """
    pid = problem.get("id") or problem.get("_id") or ""
    difficulty = problem.get("difficulty", "Easy")

    if pid in completed_ids:
        return "✅", "Completed"

    if pid == active_problem_id:
        return "🔄", "Recommended"

    if pid in remediation_problem_ids:
        return "⭐", "Stretch Goal"

    if difficulty == "Hard":
        return "🔴", "Advanced"

    if difficulty == "Medium":
        return "⭐", "Stretch Goal"

    return "○", "Not Started"


def should_show_banner(problem: dict) -> bool:
    """Show an informational banner when opening a difficult problem the learner hasn't done yet."""
    pid = problem.get("id") or problem.get("_id") or ""
    difficulty = problem.get("difficulty", "Easy")
    return difficulty == "Hard" and pid not in completed_ids


# ─── Section: Curated Problems (Phase 3) ──────────────────────────────────────

st.markdown('<div class="section-header">🏁 Curated Problems</div>', unsafe_allow_html=True)

# Partition: fixed (curated) vs generated (AI) problems
fixed_problems = []
for p in problems:
    # Generated problems have a user_id; skip them here
    if not p.get("user_id"):
        fixed_problems.append(p)

if not fixed_problems:
    st.info("No curated problems found for this topic yet.")

for idx, problem in enumerate(fixed_problems):
    status_emoji, status_label = get_problem_status(problem)
    pid = problem.get("id") or problem.get("_id") or ""

    with st.container():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(
                f"""
                <div class="problem-card">
                    <span class="badge-fixed">CURATED ROADMAP</span>
                    <span style="margin-left: 8px; font-size: 13px; color: #8B949E;">{status_emoji} {status_label}</span>
                    <div class="problem-title">{problem['title']}</div>
                    <div class="problem-difficulty">
                        Difficulty: {problem.get('difficulty', 'Unknown')}
                        &nbsp;|&nbsp; Topic: {problem.get('subtopic', problem.get('topic', ''))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.write("")
            st.write("")

            # Phase 1: NEVER lock. Always allow solving.
            if st.button("Solve 🚀", key=f"solve_fixed_{idx}", use_container_width=True):
                # Phase 1: informational banner before opening hard unsolved problems
                if should_show_banner(problem):
                    prereqs = [p["title"] for p in fixed_problems if p.get("difficulty") in ("Easy", "Medium") and (p.get("id") or p.get("_id", "")) not in completed_ids]
                    prereq_text = prereqs[0] if prereqs else None
                    st.session_state["difficulty_banner"] = {
                        "show": True,
                        "prereq": prereq_text,
                    }
                else:
                    st.session_state.pop("difficulty_banner", None)

                navigate_to_problem(problem)


# ─── Section: AI Practice (Phase 3) ───────────────────────────────────────────

st.markdown('<div class="section-header">🤖 AI Practice</div>', unsafe_allow_html=True)

if ai_practice_history:
    for idx, ai_practice in enumerate(ai_practice_history):
        ai_pid = ai_practice.get("problem_id") or ai_practice.get("id") or ai_practice.get("_id") or ""
        ai_completed = ai_pid in completed_ids
        ai_difficulty = ai_practice.get("difficulty", "Medium")
        ai_weakness = ai_practice.get("weakness", "")
        ai_reason = ai_practice.get("reason") or "Personalized practice generated for your current weakness."
        ai_objective = ai_practice.get("learning_objective") or "Strengthen your understanding of the intended concept."
        generated_at = ai_practice.get("generated_at") or ai_practice.get("created_at") or ""
        status_label = "Completed" if ai_completed else "Pending"
        highlight = "border: 2px solid #A78BFA;" if idx == 0 else ""

        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                completion_indicator = "✅ Completed" if ai_completed else "🔄 Current Recommended Practice" if idx == 0 else "📝 Practice History"
                st.markdown(
                    f"""
                    <div class="ai-practice-card" style="{highlight}">
                        <span class="badge-ai">AI PRACTICE</span>
                        <span style="margin-left: 8px; font-size: 13px; color: #A78BFA;">{completion_indicator}</span>
                        <div class="problem-title" style="margin-top: 8px;">{ai_practice.get('title', 'AI Challenge')}</div>
                        <div class="problem-difficulty">
                            Difficulty: <b>{ai_difficulty}</b>
                            {f'&nbsp;|&nbsp; Targeting: <b>{ai_weakness}</b>' if ai_weakness else ''}
                        </div>
                        <div style="margin-top: 8px; font-size: 13px; color: #C7D2FE;">
                            Generated: {generated_at}
                        </div>
                        <div style="margin-top: 6px; font-size: 13px; color: #E2E8F0;">
                            Reason: {ai_reason}
                        </div>
                        <div style="margin-top: 6px; font-size: 13px; color: #94A3B8;">
                            Learning Objective: {ai_objective}
                        </div>
                        <div style="margin-top: 6px; font-size: 13px; color: #94A3B8;">
                            Status: {status_label}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.write("")
                st.write("")
                if st.button("Solve 🚀", key=f"solve_ai_practice_{idx}", use_container_width=True):
                    st.session_state.pop("difficulty_banner", None)
                    navigate_to_problem(ai_practice)
else:
    st.markdown(
        """
        <div style="background: #0f1420; border: 1px dashed #7C3AED; border-radius: 12px; padding: 24px; text-align: center; color: #64748B;">
            <div style="font-size: 32px; margin-bottom: 8px;">🤖</div>
            <div style="font-size: 16px; font-weight: 600; color: #A78BFA; margin-bottom: 4px;">No AI Practice Yet</div>
            <div style="font-size: 14px;">Solve a curated problem above to unlock a personalized AI challenge!</div>
        </div>
        """,
        unsafe_allow_html=True,
    )