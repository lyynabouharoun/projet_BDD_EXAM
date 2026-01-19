import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database import fetch_prof_schedule

def prof_dashboard(user):
    schedule = fetch_prof_schedule(user["id"])
    
    st.markdown(f"<h2>Welcome {user['nom']} (Professor)</h2>", unsafe_allow_html=True)
    st.write("### Your Exam Schedule")
    st.dataframe(schedule)
