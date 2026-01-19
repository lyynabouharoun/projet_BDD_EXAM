import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database import fetch_department_schedule, approve_department_schedule

def chef_dashboard(user):
    st.markdown(f"<h2>Welcome {user['nom']} (Chef de Département)</h2>", unsafe_allow_html=True)
    
    schedule = fetch_department_schedule(user["departement_id"])
    
    st.write("### Department Exam Schedule")
    st.dataframe(schedule)
    
    if st.button("Approve Schedule"):
        approve_department_schedule(user["departement_id"])
        st.success("✅ Schedule approved, sent to Doyen")
