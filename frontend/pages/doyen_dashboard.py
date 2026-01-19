import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database import fetch_all_departments_schedule, approve_final_schedule

def doyen_dashboard(user):
    st.markdown(f"<h2>Welcome {user['nom']} (Doyen)</h2>", unsafe_allow_html=True)
    
    schedule = fetch_all_departments_schedule()
    
    st.write("### All Departments Exam Schedule")
    st.dataframe(schedule)
    
    if st.button("Approve All Schedules"):
        approve_final_schedule()
        st.success("✅ All schedules approved")
