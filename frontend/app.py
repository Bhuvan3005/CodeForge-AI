import streamlit as st
import requests

st.title("Hello Please Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

BASE_URL = "http://localhost:8000"

if st.button("Login"):
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": email,
                "password": password
            }
        )
        
        print(response.text)

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
            
            st.switch_page("pages/dashboard.py")
        else:
            try:
                detail = response.json().get("detail", "Login failed")
            except:
                detail = f"Error: {response.status_code}"
            st.error(detail)
    
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        
        
        
        
        
        

if st.button("Register"):
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": password
            }
        )

        if response.status_code == 200:
            st.success("Registration successful! Please login.")
        else:
            try:
                detail = response.json().get("detail", "Registration failed")
            except:
                detail = f"Error: {response.status_code}"
            st.error(detail)
    except Exception as e:
        st.error(f"Error: {str(e)}")

    if response.status_code == 200:
        st.success("Registered successfully")

    else:
        st.error(response.json()["detail"])