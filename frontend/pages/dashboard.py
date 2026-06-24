import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="CodeForge - Dashboard", page_icon="💻", layout="wide")

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]

# Verify session and get user details
response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code != 200:
    st.error("Session expired")
    st.stop()

user = response.json()

# Custom premium styling
st.markdown("""
<style>
.main-header {
    font-size: 40px;
    font-weight: 800;
    background: linear-gradient(45deg, #FF4B4B, #FF8F8F);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}
.sub-header {
    font-size: 18px;
    color: #666;
    margin-bottom: 25px;
}
.stat-card {
    background: #0E1117;
    border: 1px solid #30363D;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}
.skill-bar-container {
    background-color: #30363D;
    border-radius: 10px;
    margin-bottom: 10px;
    height: 12px;
    width: 100%;
}
.skill-bar-fill {
    background: linear-gradient(90deg, #10B981, #3B82F6);
    height: 100%;
    border-radius: 10px;
}
.skill-label {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# Layout: Sidebar & Content
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/code.png", width=100)
    st.markdown("### CodeForge AI Mentor")
    st.write(f"Logged in as: **{user['email']}**")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

# Main Dashboard Content
st.markdown('<div class="main-header">CodeForge AI Mentor Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Personalized, adaptive DSA roadmap and skill profile tracker</div>', unsafe_allow_html=True)

# Fetch Roadmap & Skill Profile
with st.spinner("Loading your profile..."):
    roadmap_resp = requests.get(f"{BASE_URL}/roadmap/status", headers={"Authorization": f"Bearer {token}"})
    profile_resp = requests.get(f"{BASE_URL}/roadmap/profile", headers={"Authorization": f"Bearer {token}"})
    remediation_resp = requests.get(f"{BASE_URL}/roadmap/remediation", headers={"Authorization": f"Bearer {token}"})

roadmap = roadmap_resp.json() if roadmap_resp.status_code == 200 else {}
profile = profile_resp.json() if profile_resp.status_code == 200 else {}
remediation = remediation_resp.json() if remediation_resp.status_code == 200 else {}

# Top Grid: Status & Actions
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.subheader("🏁 Current Progress")
    current_topic = roadmap.get("current_topic", "Arrays")
    fixed_idx = roadmap.get("current_fixed_question_index", 0)
    
    st.markdown(f"Current Topic: **{current_topic}**")
    st.markdown(f"Curated Question Progress: **{fixed_idx}/3 completed**")
    
    if st.button("📚 Resume Learning Path", type="primary", use_container_width=True):
        st.session_state["selected_topic"] = current_topic
        st.switch_page("pages/Topic_detail.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.subheader("⚠️ Remediation Mode")
    
    is_active = remediation.get("remediation_active", False)
    if is_active:
        problems = remediation.get("problems", [])
        st.error(f"Mentor Alert: You have **{len(problems)}** pending remediation exercise(s) to solve!")
        
        # Display the remediation problems
        for idx, prob in enumerate(problems, 1):
            if st.button(f"✏️ Solve Practice {idx}: {prob['title']}", key=f"dash_rem_{idx}", use_container_width=True):
                st.session_state["selected_problem"] = prob
                st.switch_page("pages/Problem_details.py")
    else:
        st.success("You are fully caught up with no pending weaknesses!")
        if st.button("🗺️ Browse All Topics", use_container_width=True):
            st.switch_page("pages/Learning_Path.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Skill Mastery Section
st.header("📈 Your Skill Profile")
mastery_scores = profile.get("mastery_scores", {})

if not mastery_scores:
    st.info("Start solving problems to build your personalized skill profile!")
else:
    for topic, subtopics in mastery_scores.items():
        if subtopics:
            with st.expander(f"📚 {topic} Mastery", expanded=True):
                cols = st.columns(2)
                for i, (subtopic, score) in enumerate(subtopics.items()):
                    col_target = cols[i % 2]
                    with col_target:
                        st.markdown(
                            f"""
                            <div class="skill-label">
                                <span>{subtopic}</span>
                                <span>{score}%</span>
                            </div>
                            <div class="skill-bar-container">
                                <div class="skill-bar-fill" style="width: {score}%;"></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )