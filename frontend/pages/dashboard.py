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

st.title("Dashboard")

st.write("Welcome")
st.write(user["email"])

if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("app.py")