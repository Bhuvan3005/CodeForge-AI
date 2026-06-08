import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

if not st.session_state.get("logged_in"):
    st.error("Please login first")
    st.stop()

token = st.session_state["token"]

response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={
        "Authorization": f"Bearer {token}"
    }
)

if response.status_code != 200:
    st.error("Session expired")
    st.stop()

user = response.json()


st.markdown("""
<style>
.topic-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #e0e0e0;
    margin-bottom: 15px;
    background-color: blue;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}
.topic-title {
    font-size: 24px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Learning Topics")

for idx, topic in enumerate(st.session_state["topics"]):

    with st.container():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(
                f"""
                <div class="topic-card">
                    <div class="topic-title">{topic}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            if st.button("Continue ➜", key=f"continue_{idx}"):
                st.session_state["selected_topic"] = topic
                st.switch_page("pages/Topic_detail.py")
    
    
    