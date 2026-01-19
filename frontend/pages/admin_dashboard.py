# frontend/pages/admin_dashboard.py

import streamlit as st
import sys
import os
from datetime import date

# ==============================
# FIX SYSTEM PATH
# ==============================
# Add the project root to sys.path so Python can find backend/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ==============================
# IMPORT BACKEND MODULES
# ==============================
from backend.database import fetch_admin_dashboard_data
from backend.optimizer import generate_exam_schedule


def admin_dashboard(user):
    st.markdown(f"<h2>👨‍💼 Welcome {user['nom']} (Admin)</h2>", unsafe_allow_html=True)
    st.divider()

    # ==============================
    # EXAM GENERATION SECTION
    # ==============================
    st.subheader("🗓 Generate Global Exam Schedule")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start date", value=date.today())

    with col2:
        end_date = st.date_input("End date")

    if start_date >= end_date:
        st.warning("⚠️ End date must be after start date")

    if st.button("⚙️ Generate Exam Schedule"):
        if start_date < end_date:
            with st.spinner("Generating exam schedule..."):
                generate_exam_schedule(start_date, end_date)
            st.success("✅ Exam schedule generated successfully")
            st.info("📌 The schedule is now available for Chef de Département validation")

    st.divider()

    # ==============================
    # DASHBOARD ANALYTICS
    # ==============================
    data = fetch_admin_dashboard_data()

    st.subheader("🏫 Room Usage")
    st.dataframe(data["rooms"], use_container_width=True)

    st.subheader("👨‍🏫 Professors Workload")
    st.dataframe(data["professors"], use_container_width=True)

    st.subheader("⚠️ Students Conflicts")
    st.dataframe(data["student_conflicts"], use_container_width=True)