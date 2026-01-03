import streamlit as st
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database import (
    fetch_formations,
    fetch_modules_by_formation,
    fetch_students_by_formation,
    fetch_professors,
    fetch_rooms,
    fetch_all_exams,
    clear_existing_exams
)
from backend.optimizer import generate_exam_schedule

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🎯",
    layout="wide"
)

# =====================================
# HEADER
# =====================================

st.title("🎯 Admin Dashboard")
st.markdown("---")

# =====================================
# SIDEBAR - ADMIN MENU
# =====================================

st.sidebar.title("Admin Menu")
admin_choice = st.sidebar.radio(
    "Select Action:",
    ["Dashboard Overview", "Manage Formations", "Manage Modules", 
     "Manage Professors", "Manage Rooms", "Generate Schedule"]
)

st.sidebar.markdown("---")

# =====================================
# DASHBOARD OVERVIEW
# =====================================

if admin_choice == "Dashboard Overview":
    st.header("📊 System Overview")
    
    try:
        formations = fetch_formations()
        professors = fetch_professors()
        rooms = fetch_rooms()
        exams = fetch_all_exams()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="📚 Formations", value=len(formations))
        
        with col2:
            st.metric(label="👨‍🏫 Professors", value=len(professors))
        
        with col3:
            st.metric(label="🏛️ Rooms", value=len(rooms))
        
        with col4:
            st.metric(label="📝 Scheduled Exams", value=len(exams))
        
        st.markdown("---")
        
        # Recent Exams
        st.subheader("📅 Recent Scheduled Exams")
        if exams:
            st.dataframe(exams[:20], use_container_width=True)
        else:
            st.info("No exams scheduled yet. Use 'Generate Schedule' to create a schedule.")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

# =====================================
# MANAGE FORMATIONS
# =====================================

elif admin_choice == "Manage Formations":
    st.header("📚 Manage Formations")
    
    try:
        formations = fetch_formations()
        
        if formations:
            st.subheader("Existing Formations")
            
            # Display as table
            formation_data = []
            for f in formations:
                formation_data.append({
                    "ID": f["id"],
                    "Name": f["nom"],
                    "Cycle": f["cycle"],
                    "Level": f["niveau"],
                    "Department ID": f["departement_id"]
                })
            
            st.dataframe(formation_data, use_container_width=True)
            
            # Formation details
            st.markdown("---")
            st.subheader("Formation Details")
            
            selected_formation = st.selectbox(
                "Select Formation:",
                options=[f["id"] for f in formations],
                format_func=lambda x: next(f["nom"] for f in formations if f["id"] == x)
            )
            
            if selected_formation:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Modules:**")
                    modules = fetch_modules_by_formation(selected_formation)
                    if modules:
                        for m in modules:
                            st.write(f"- {m['nom']} (Semester {m['semestre']})")
                    else:
                        st.info("No modules found")
                
                with col2:
                    st.markdown("**Students:**")
                    students = fetch_students_by_formation(selected_formation)
                    st.write(f"Total: {len(students)} students")
        else:
            st.warning("No formations found in database")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# =====================================
# MANAGE MODULES
# =====================================

elif admin_choice == "Manage Modules":
    st.header("📖 Manage Modules")
    
    try:
        formations = fetch_formations()
        
        if formations:
            selected_formation = st.selectbox(
                "Select Formation:",
                options=[f["id"] for f in formations],
                format_func=lambda x: next(f["nom"] for f in formations if f["id"] == x)
            )
            
            if selected_formation:
                modules = fetch_modules_by_formation(selected_formation)
                
                if modules:
                    st.subheader(f"Modules for {next(f['nom'] for f in formations if f['id'] == selected_formation)}")
                    
                    module_data = []
                    for m in modules:
                        module_data.append({
                            "ID": m["id"],
                            "Name": m["nom"],
                            "Semester": m["semestre"],
                            "Credits": m.get("credits", "N/A")
                        })
                    
                    st.dataframe(module_data, use_container_width=True)
                else:
                    st.info("No modules found for this formation")
        else:
            st.warning("No formations found")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# =====================================
# MANAGE PROFESSORS
# =====================================

elif admin_choice == "Manage Professors":
    st.header("👨‍🏫 Manage Professors")
    
    try:
        professors = fetch_professors()
        
        if professors:
            st.subheader("All Professors")
            
            prof_data = []
            for p in professors:
                prof_data.append({
                    "ID": p["id"],
                    "Name": p["nom"],
                    "Specialty": p.get("specialite", "N/A"),
                    "Department ID": p.get("departement_id", "N/A")
                })
            
            st.dataframe(prof_data, use_container_width=True)
        else:
            st.warning("No professors found")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# =====================================
# MANAGE ROOMS
# =====================================

elif admin_choice == "Manage Rooms":
    st.header("🏛️ Manage Rooms")
    
    try:
        rooms = fetch_rooms()
        
        if rooms:
            st.subheader("All Rooms")
            
            room_data = []
            for r in rooms:
                room_data.append({
                    "ID": r["id"],
                    "Name": r["nom"],
                    "Capacity": r.get("capacite", "N/A"),
                    "Type": r.get("type", "N/A"),
                    "Building ID": r.get("batiment_id", "N/A")
                })
            
            st.dataframe(room_data, use_container_width=True)
            
            # Room statistics
            st.markdown("---")
            st.subheader("📊 Room Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                total_capacity = sum(r.get("capacite", 0) for r in rooms)
                st.metric("Total Capacity", total_capacity)
            
            with col2:
                amphi_count = sum(1 for r in rooms if r.get("type") == "AMPHI")
                st.metric("Amphitheaters", amphi_count)
        else:
            st.warning("No rooms found")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# =====================================
# GENERATE SCHEDULE
# =====================================

elif admin_choice == "Generate Schedule":
    st.header("🔄 Generate Exam Schedule")
    
    st.warning("⚠️ This will delete all existing exams and generate a new schedule!")
    
    st.markdown("""
    ### Scheduling Parameters:
    - **Exam Duration**: 90 minutes
    - **Time Slots**: 8:30 AM, 10:30 AM, 1:30 PM
    - **Excluded Days**: Fridays
    - **Date Range**: January 6 - January 21, 2026
    
    ### Constraints:
    - No student has multiple exams on the same day
    - No room conflicts
    - No Friday exams
    - Each module scheduled exactly once
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🚀 Generate Schedule", type="primary"):
            with st.spinner("Generating schedule... This may take a few minutes."):
                try:
                    generate_exam_schedule()
                    st.success("✅ Schedule generated successfully!")
                    st.balloons()
                    
                    # Show results
                    st.markdown("---")
                    exams = fetch_all_exams()
                    st.subheader(f"📊 Results: {len(exams)} exams scheduled")
                    
                    if exams:
                        st.dataframe(exams[:50], use_container_width=True)
                        
                except Exception as e:
                    st.error(f"❌ Error generating schedule: {str(e)}")
                    st.exception(e)

# =====================================
# FOOTER
# =====================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Admin Dashboard | Exam Planning System</p>
</div>
""", unsafe_allow_html=True)