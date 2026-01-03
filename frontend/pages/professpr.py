import streamlit as st
import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.database import fetch_professors, get_connection

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Professor Portal",
    page_icon="👨‍🏫",
    layout="wide"
)

# =====================================
# HEADER
# =====================================

st.title("👨‍🏫 Professor Portal")
st.markdown("---")

# =====================================
# HELPER FUNCTIONS
# =====================================

def get_professor_exams(prof_id):
    """Get all exams assigned to a professor"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            e.id,
            m.nom AS module,
            f.nom AS formation,
            s.nom AS salle,
            e.date_exam,
            e.heure_debut,
            e.duree_minutes
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN salles s ON e.salle_id = s.id
        WHERE e.prof_id = %s
        ORDER BY e.date_exam, e.heure_debut
    """, (prof_id,))
    
    exams = cur.fetchall()
    
    # Convert to list of dicts
    columns = ['id', 'module', 'formation', 'salle', 'date_exam', 'heure_debut', 'duree_minutes']
    result = []
    for exam in exams:
        result.append(dict(zip(columns, exam)))
    
    cur.close()
    conn.close()
    
    return result


def get_professor_workload(prof_id):
    """Get professor's exam count and total hours"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            COUNT(*) as exam_count,
            SUM(duree_minutes) as total_minutes
        FROM examens
        WHERE prof_id = %s
    """, (prof_id,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    return result


def get_students_for_exam(module_id):
    """Get number of students enrolled in a module"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT COUNT(*) 
        FROM inscriptions
        WHERE module_id = %s
    """, (module_id,))
    
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    return count


# =====================================
# PROFESSOR SELECTION
# =====================================

try:
    professors = fetch_professors()
    
    if not professors:
        st.warning("No professors found in the database.")
        st.stop()
    
    st.subheader("Select Professor")
    
    # Create selection
    professor_names = {p["id"]: p["nom"] for p in professors}
    
    selected_prof_id = st.selectbox(
        "Choose your profile:",
        options=list(professor_names.keys()),
        format_func=lambda x: professor_names[x]
    )
    
    if selected_prof_id:
        selected_prof = next(p for p in professors if p["id"] == selected_prof_id)
        
        st.markdown("---")
        
        # =====================================
        # PROFESSOR INFO
        # =====================================
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Name:** {selected_prof['nom']}")
        
        with col2:
            st.markdown(f"**Specialty:** {selected_prof.get('specialite', 'N/A')}")
        
        with col3:
            st.markdown(f"**Department ID:** {selected_prof.get('departement_id', 'N/A')}")
        
        st.markdown("---")
        
        # =====================================
        # WORKLOAD STATISTICS
        # =====================================
        
        st.subheader("📊 Workload Statistics")
        
        workload = get_professor_workload(selected_prof_id)
        exam_count = workload[0] if workload else 0
        total_minutes = workload[1] if workload and workload[1] else 0
        total_hours = total_minutes / 60
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📝 Total Exams",
                value=exam_count
            )
        
        with col2:
            st.metric(
                label="⏱️ Total Hours",
                value=f"{total_hours:.1f} hrs"
            )
        
        with col3:
            avg_duration = total_minutes / exam_count if exam_count > 0 else 0
            st.metric(
                label="📏 Avg Duration",
                value=f"{avg_duration:.0f} min"
            )
        
        st.markdown("---")
        
        # =====================================
        # EXAM SCHEDULE
        # =====================================
        
        st.subheader("📅 Your Exam Schedule")
        
        exams = get_professor_exams(selected_prof_id)
        
        if exams:
            # Display as cards or table
            display_mode = st.radio(
                "Display Mode:",
                ["Table View", "Card View"],
                horizontal=True
            )
            
            if display_mode == "Table View":
                # Create DataFrame
                df = pd.DataFrame(exams)
                df = df[['date_exam', 'heure_debut', 'module', 'formation', 'salle', 'duree_minutes']]
                df.columns = ['Date', 'Time', 'Module', 'Formation', 'Room', 'Duration (min)']
                
                st.dataframe(df, use_container_width=True)
                
            else:  # Card View
                for i, exam in enumerate(exams):
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"### 📖 {exam['module']}")
                            st.markdown(f"**Formation:** {exam['formation']}")
                        
                        with col2:
                            st.markdown(f"**📅 Date:** {exam['date_exam']}")
                            st.markdown(f"**🕐 Time:** {exam['heure_debut']}")
                            st.markdown(f"**⏱️ Duration:** {exam['duree_minutes']} min")
                        
                        with col3:
                            st.markdown(f"**🏛️ Room:**")
                            st.markdown(f"{exam['salle']}")
                        
                        st.markdown("---")
            
            # =====================================
            # DOWNLOAD SCHEDULE
            # =====================================
            
            st.markdown("### 📥 Download Schedule")
            
            # Create CSV
            df_export = pd.DataFrame(exams)
            df_export = df_export[['date_exam', 'heure_debut', 'module', 'formation', 'salle', 'duree_minutes']]
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"schedule_{selected_prof['nom']}.csv",
                mime="text/csv"
            )
            
        else:
            st.info("📭 No exams assigned yet.")
            st.markdown("""
            **Possible reasons:**
            - The schedule hasn't been generated yet
            - No modules have been assigned to you
            - The exam period hasn't started
            
            Please contact the administrator if you believe this is an error.
            """)
        
        st.markdown("---")
        
        # =====================================
        # UPCOMING EXAMS
        # =====================================
        
        if exams:
            st.subheader("🔔 Upcoming Exams")
            
            from datetime import datetime, timedelta
            today = datetime.now().date()
            week_later = today + timedelta(days=7)
            
            upcoming = [e for e in exams if today <= e['date_exam'] <= week_later]
            
            if upcoming:
                st.success(f"You have {len(upcoming)} exam(s) in the next 7 days:")
                
                for exam in upcoming:
                    st.markdown(f"""
                    - **{exam['module']}** on {exam['date_exam']} at {exam['heure_debut']} 
                      in room {exam['salle']}
                    """)
            else:
                st.info("No exams scheduled in the next 7 days.")

except Exception as e:
    st.error(f"❌ Error loading professor data: {str(e)}")
    st.exception(e)

# =====================================
# FOOTER
# =====================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Professor Portal | Exam Planning System</p>
</div>
""", unsafe_allow_html=True)