import streamlit as st
import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database import (
    validate_staff_login,
    validate_student_login,
    validate_prof_login
)


def login_page():
    st.title("🔐 Exam Planning System")

    login_type = st.radio(
        "Login as:",
        ["Staff", "Professor", "Student"]
    )

    # =========================
    # STAFF LOGIN
    # =========================
    if login_type == "Staff":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = validate_staff_login(email, password)
            if user:
                st.session_state["user"] = user
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid staff credentials")

    # =========================
    # PROFESSOR LOGIN
    # =========================
    elif login_type == "Professor":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = validate_prof_login(email, password)
            if user:
                st.session_state["user"] = user
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid professor credentials")

    # =========================
    # STUDENT LOGIN
    # =========================
    else:
        matricule = st.text_input("Matricule")
        birth_date = st.date_input(
            "Date de naissance",
            min_value=date(1950, 1, 1),
            max_value=date.today()
        )

        if st.button("Login"):
            user = validate_student_login(matricule, str(birth_date))
            if user:
                user["role"] = "student"
                st.session_state["user"] = user
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid student credentials")
