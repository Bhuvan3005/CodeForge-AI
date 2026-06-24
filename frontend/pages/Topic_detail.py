import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="CodeForge - Topic Details", page_icon="📚", layout="wide")

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]
topic = st.session_state.get("selected_topic")

if not topic:
    st.error("No topic selected")
    st.stop()

# Verify session and get user details
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

# Fetch user's remediation status
remediation_resp = requests.get(
    f"{BASE_URL}/roadmap/remediation",
    headers={"Authorization": f"Bearer {token}"}
)
remediation = remediation_resp.json() if remediation_resp.status_code == 200 else {}
is_remediation_active = remediation.get("remediation_active", False)

# Fetch all problems (both preseeded fixed ones and any generated remediation ones)
response = requests.get(
    f"{BASE_URL}/problems/{topic}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code != 200:
    st.error("Failed to fetch problems")
    st.stop()

problems = response.json()

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
.badge-remediation {
    background: #FF4B4B;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

if is_remediation_active:
    st.error("⚠️ **Remediation Lock Active:** Solve the AI-generated practice problem(s) below to continue your roadmap.")

st.subheader("Problems List")

# Partition problems into fixed and remediation
fixed_problems = []
remediation_problems = []

for p in problems:
    # If a problem has a user_id, it is a custom-generated remediation problem
    if p.get("user_id"):
        remediation_problems.append(p)
    else:
        fixed_problems.append(p)

# Render Remediation Problems first if they exist
if remediation_problems:
    st.markdown("#### 🎯 Targeted Remediation Problems")
    for idx, problem in enumerate(remediation_problems):
        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(
                    f"""
                    <div class="remediation-card">
                        <span class="badge-remediation">AI PRACTICE</span>
                        <div class="problem-title">{problem['title']}</div>
                        <div class="problem-difficulty">
                            Difficulty: {problem.get('difficulty', 'Unknown')} | Weakness Targeted: <b>{problem.get('weakness', 'General')}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                # Spacer
                st.write("")
                st.write("")
                if st.button("Solve 🚀", key=f"solve_rem_{idx}"):
                    st.session_state["selected_problem"] = problem
                    st.switch_page("pages/Problem_details.py")

# Render Fixed Problems
st.markdown("#### 🏁 Standard Curated Roadmap")
for idx, problem in enumerate(fixed_problems):
    # If remediation is active, standard roadmap problems are locked
    is_locked = is_remediation_active

    with st.container():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(
                f"""
                <div class="problem-card" style="opacity: {0.5 if is_locked else 1.0};">
                    <span class="badge-fixed">CURATED ROADMAP</span>
                    <div class="problem-title">{problem['title']}</div>
                    <div class="problem-difficulty">
                        Difficulty: {problem.get('difficulty', 'Unknown')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.write("")
            st.write("")
            if is_locked:
                st.button("🔒 Locked", key=f"solve_fixed_{idx}", disabled=True, use_container_width=True)
            else:
                if st.button("Solve 🚀", key=f"solve_fixed_{idx}", use_container_width=True):
                    st.session_state["selected_problem"] = problem
                    st.switch_page("pages/Problem_details.py")