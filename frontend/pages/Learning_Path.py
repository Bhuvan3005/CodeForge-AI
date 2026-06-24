import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="CodeForge - Learning Path", page_icon="📚", layout="wide")

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]

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
    st.title("📚 Learning Topics")
    st.caption("Select a topic from the curriculum roadmap to start practicing.")
with col_back:
    if st.button("⬅ Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

# Custom styling for topic cards
st.markdown("""
<style>
.topic-card {
    background: #0E1117;
    border: 1px solid #30363D;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s, border-color 0.2s;
}
.topic-card:hover {
    transform: translateY(-2px);
    border-color: #3B82F6;
}
.topic-title {
    font-size: 24px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# List of topics
topics = st.session_state.get("topics", [])

for idx, topic in enumerate(topics):
    with st.container():
        col_card, col_btn = st.columns([5, 1])

        with col_card:
            st.markdown(
                f"""
                <div class="topic-card">
                    <div class="topic-title">{topic}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_btn:
            st.write("")
            st.write("")
            if st.button("Explore ➜", key=f"continue_{idx}", use_container_width=True):
                st.session_state["selected_topic"] = topic
                st.switch_page("pages/Topic_detail.py")