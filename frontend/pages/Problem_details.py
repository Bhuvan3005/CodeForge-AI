import streamlit as st

problem = st.session_state.get("selected_problem")

if not problem:
    st.error("No problem selected")
    st.stop()

st.title(problem["title"])

st.write(problem.get("description", ""))

st.subheader("Difficulty")
st.write(problem.get("difficulty", "Unknown"))

if st.button("⬅ Back"):
    st.switch_page("pages/topic_details.py")