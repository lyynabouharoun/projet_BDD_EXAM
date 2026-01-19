import streamlit as st
from backend.database import (
    validate_staff_login,
    validate_student_login
)

def login_user(login_type, identifier, password):
    """
    login_type: 'staff' | 'student'
    """

    if login_type == "staff":
        user = validate_staff_login(identifier, password)
        if user:
            st.session_state["user"] = {
                "id": user["id"],
                "nom": user["nom"],
                "prenom": user["prenom"],
                "role": user["role"].lower()
            }
            return True

    elif login_type == "student":
        user = validate_student_login(identifier, password)
        if user:
            st.session_state["user"] = {
                "id": user["id"],
                "nom": user["nom"],
                "prenom": user["prenom"],
                "role": "student",
                "formation_id": user["formation_id"]
            }
            return True

    return False
