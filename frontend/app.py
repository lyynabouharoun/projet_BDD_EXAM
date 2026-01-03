import streamlit as st
from backend.database import (
    fetch_formations,
    fetch_modules_by_formation,
    fetch_students_by_formation,
    fetch_all_exams
)

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Exam Planning System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #0066cc;
        color: white;
    }
    
    .stButton>button:hover {
        background-color: #0052a3;
        color: white;
    }
    
    h1 {
        color: #0066cc;
        padding-bottom: 1rem;
    }
    
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #0066cc;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================
# MAIN PAGE
# =====================================

st.title("📚 Exam Planning System")
st.markdown("---")

st.markdown("""
### Welcome to the Exam Planning System

This application helps manage and optimize exam schedules for the Faculty of Science.

#### Features:
- 🎯 **Admin Dashboard**: Manage departments, formations, modules, and generate schedules
- 👨‍🏫 **Professor Portal**: View assigned exams and manage availability
- 👨‍🎓 **Student Portal**: View personal exam schedule
- 📊 **Dashboard**: View statistics and system overview

#### Navigation:
Use the sidebar to navigate between different sections of the application.

#### System Information:
- **Database**: PostgreSQL
- **Scheduling Algorithm**: Constraint-based optimizer
- **Time Slots**: 8:30 AM, 10:30 AM, 1:30 PM
- **Exam Duration**: 90 minutes
- **Constraints**: No Friday exams, no student conflicts, room capacity checks
""")

st.markdown("---")

# =====================================
# QUICK STATS (DYNAMIC FROM DATABASE)
# =====================================

# Fetch data from DB
formations = fetch_formations()
modules = []
students = set()

for f in formations:
    mods = fetch_modules_by_formation(f["id"])
    modules.extend(mods)
    studs = fetch_students_by_formation(f["id"])
    for s in studs:
        students.add(s["id"])  # using set to avoid duplicates

exams = fetch_all_exams()

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📚 Total Formations", value=len(formations))
with col2:
    st.metric(label="📖 Total Modules", value=len(modules))
with col3:
    st.metric(label="👨‍🎓 Total Students", value=len(students))
with col4:
    st.metric(label="📝 Scheduled Exams", value=len(exams))

st.markdown("---")

st.info("👈 Use the sidebar to navigate to different pages")

# =====================================
# FOOTER
# =====================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Exam Planning System | Faculty of Science | 2026</p>
</div>
""", unsafe_allow_html=True)
