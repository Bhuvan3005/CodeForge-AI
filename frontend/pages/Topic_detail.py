import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]
topic = st.session_state.get("selected_topic")

if not topic:
    st.error("No topic selected")
    st.stop()

# Verify user
response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code != 200:
    st.error("Session expired")
    st.stop()

st.set_page_config(page_title=f"{topic} Problems")

st.title(f"📚 {topic}")

# Fetch problems
response = requests.get(
    f"{BASE_URL}/problems/{topic}",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code != 200:
    st.error("Failed to fetch problems")
    st.stop()

problems = response.json()

# CSS
st.markdown("""
<style>
.problem-card {
    background: blue;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    border: 1px solid #ddd;
}
.problem-title {
    font-size: 22px;
    font-weight: bold;
}
.problem-difficulty {
    color: #666;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

for idx, problem in enumerate(problems):

    with st.container():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(
                f"""
                <div class="problem-card">
                    <div class="problem-title">
                        {problem['title']}
                    </div>
                    <div class="problem-difficulty">
                        Difficulty: {problem.get('difficulty', 'Unknown')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            if st.button("Solve 🚀", key=f"solve_{idx}"):

                st.session_state["selected_problem"] = problem

                st.switch_page("pages/problem_details.py")