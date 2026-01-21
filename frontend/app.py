import streamlit as st
import sys
import os
import psycopg2

# Connect to the database using the secret
try:
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    st.success("Connected to the database!")
except Exception as e:
    st.error(f"Database connection failed: {e}")

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pages.login import login_page
from pages.admin_dashboard import admin_dashboard
from pages.chef_dashboard import chef_dashboard
from pages.doyen_dashboard import doyen_dashboard
from pages.student_dashboard import student_dashboard
from pages.prof_dashboard import prof_dashboard

st.set_page_config(page_title="Exam Planning System", layout="wide")

if "user" not in st.session_state:
    login_page()
else:
    user = st.session_state["user"]
    role = user.get("role", "")

    if role == "ADMIN":
        admin_dashboard(user)
    elif role == "CHEF_DEPARTEMENT":
        chef_dashboard(user)
    elif role in ["DOYEN", "VICE_DOYEN"]:
        doyen_dashboard(user)
    elif role == "student":
        student_dashboard(user)
    elif role == "prof":
        prof_dashboard(user)
    else:
        st.error("⚠️ Unknown role. Contact admin.")

