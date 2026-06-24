import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="CodeForge - Login", page_icon="💻", layout="centered")

# Custom visual styling for login/register page
st.markdown("""
<style>
.title-container {
    text-align: center;
    padding: 30px 0;
    margin-bottom: 20px;
}
.brand-name {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(45deg, #FF4B4B, #FF8F8F);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.tagline {
    color: #8B949E;
    font-size: 16px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-container">
    <div class="brand-name">CodeForge</div>
    <div class="tagline">An Adaptive, AI-Powered DSA Learning Engine</div>
</div>
""", unsafe_allow_html=True)

email = st.text_input("📧 Email Address", placeholder="name@domain.com")
password = st.text_input("🔑 Password", type="password", placeholder="Enter your secure password")

col_login, col_reg = st.columns(2)

with col_login:
    if st.button("🚀 Login", use_container_width=True, type="primary"):
        if not email or not password:
            st.warning("Please provide email and password.")
        else:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    data={
                        "username": email,
                        "password": password
                    }
                )
                if response.status_code == 200:
                    token = response.json()["access_token"]
                    st.session_state["token"] = token
                    st.session_state["logged_in"] = True
                    
                    st.session_state["topics"] = [
                        "Arrays",
                        "HashMap",
                        "Sliding Window",
                        "Two Pointers",
                        "Stack",
                        "Queue",
                        "Linked List",
                        "Trees",
                        "Graphs",
                        "Dynamic Programming",
                        "Greedy",
                        "Backtracking",
                        "Binary Search",
                        "Heap",
                        "Trie",
                        "Bit Manipulation"
                    ]
                    st.success("Login successful!")
                    st.switch_page("pages/dashboard.py")
                else:
                    try:
                        detail = response.json().get("detail", "Login failed")
                    except Exception:
                        detail = f"Error: {response.status_code}"
                    st.error(detail)
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

with col_reg:
    if st.button("📝 Register", use_container_width=True):
        if not email or not password:
            st.warning("Please provide email and password.")
        else:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json={
                        "email": email,
                        "password": password
                    }
                )
                if response.status_code == 200:
                    st.success("Registration successful! You can now login.")
                else:
                    try:
                        detail = response.json().get("detail", "Registration failed")
                    except Exception:
                        detail = f"Error: {response.status_code}"
                    st.error(detail)
            except Exception as e:
                st.error(f"Connection error: {str(e)}")