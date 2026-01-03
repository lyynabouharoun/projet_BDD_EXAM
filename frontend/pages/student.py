import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.database import get_connection

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Student Portal",
    page_icon="👨‍🎓",
    layout="wide"
)

# =====================================
# HEADER
# =====================================

st.title("👨‍🎓 Student Portal")
st.markdown("---")

# =====================================
# HELPER FUNCTIONS
# =====================================

def get_all_students():
    """Get all students from database"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.id, e.matricule, e.nom, f.nom as formation
        FROM etudiants e
        JOIN formations f ON e.formation_id = f.id
        ORDER BY e.nom
    """)
    
    students = cur.fetchall()
    
    result = []
    for s in students:
        result.append({
            'id': s[0],
            'matricule': s[1],
            'nom': s[2],
            'formation': s[3]
        })
    
    cur.close()
    conn.close()
    
    return result


def get_student_exams(student_id):
    """Get all exams for a specific student"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            m.nom AS module,
            f.nom AS formation,
            s.nom AS salle,
            e.date_exam,
            e.heure_debut,
            e.duree_minutes,
            p.nom AS professeur
        FROM inscriptions i
        JOIN modules m ON i.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN examens e ON m.id = e.module_id
        JOIN salles s ON e.salle_id = s.id
        LEFT JOIN professeurs p ON e.prof_id = p.id
        WHERE i.etudiant_id = %s
        ORDER BY e.date_exam, e.heure_debut
    """, (student_id,))
    
    exams = cur.fetchall()
    
    result = []
    for exam in exams:
        result.append({
            'module': exam[0],
            'formation': exam[1],
            'salle': exam[2],
            'date_exam': exam[3],
            'heure_debut': exam[4],
            'duree_minutes': exam[5],
            'professeur': exam[6] if exam[6] else 'TBA'
        })
    
    cur.close()
    conn.close()
    
    return result


def get_student_modules(student_id):
    """Get all modules a student is enrolled in"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.nom, m.credits, m.semestre
        FROM inscriptions i
        JOIN modules m ON i.module_id = m.id
        WHERE i.etudiant_id = %s
        ORDER BY m.semestre, m.nom
    """, (student_id,))
    
    modules = cur.fetchall()
    
    result = []
    for m in modules:
        result.append({
            'nom': m[0],
            'credits': m[1],
            'semestre': m[2]
        })
    
    cur.close()
    conn.close()
    
    return result


def check_exam_conflicts(exams):
    """Check if there are any time conflicts in student's schedule"""
    conflicts = []
    
    for i, exam1 in enumerate(exams):
        for exam2 in exams[i+1:]:
            if exam1['date_exam'] == exam2['date_exam']:
                # Same day - check if times overlap
                time1_start = exam1['heure_debut']
                time2_start = exam2['heure_debut']
                
                if time1_start == time2_start:
                    conflicts.append({
                        'date': exam1['date_exam'],
                        'time': time1_start,
                        'module1': exam1['module'],
                        'module2': exam2['module']
                    })
    
    return conflicts


# =====================================
# STUDENT SELECTION
# =====================================

try:
    students = get_all_students()
    
    if not students:
        st.warning("No students found in the database.")
        st.stop()
    
    st.subheader("Student Login")
    
    # Search/Select student
    search_option = st.radio(
        "Search by:",
        ["Name", "Student ID (Matricule)"],
        horizontal=True
    )
    
    if search_option == "Name":
        student_names = {s["id"]: f"{s['nom']} ({s['matricule']})" for s in students}
        selected_student_id = st.selectbox(
            "Select your name:",
            options=list(student_names.keys()),
            format_func=lambda x: student_names[x]
        )
    else:
        matricule_input = st.text_input("Enter your student ID (Matricule):")
        selected_student_id = None
        
        if matricule_input:
            matching_student = next((s for s in students if s['matricule'] == matricule_input), None)
            if matching_student:
                selected_student_id = matching_student['id']
                st.success(f"✅ Found: {matching_student['nom']}")
            else:
                st.error("❌ Student ID not found")
    
    if selected_student_id:
        selected_student = next(s for s in students if s["id"] == selected_student_id)
        
        st.markdown("---")
        
        # =====================================
        # STUDENT INFO
        # =====================================
        
        st.subheader("📋 Student Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Name:** {selected_student['nom']}")
        
        with col2:
            st.markdown(f"**Student ID:** {selected_student['matricule']}")
        
        with col3:
            st.markdown(f"**Formation:** {selected_student['formation']}")
        
        st.markdown("---")
        
        # =====================================
        # ENROLLED MODULES
        # =====================================
        
        st.subheader("📚 Enrolled Modules")
        
        modules = get_student_modules(selected_student_id)
        
        if modules:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Semester 1:**")
                sem1_modules = [m for m in modules if m['semestre'] == 1]
                if sem1_modules:
                    for m in sem1_modules:
                        st.write(f"- {m['nom']} ({m['credits']} credits)")
                else:
                    st.info("No modules")
            
            with col2:
                st.markdown("**Semester 2:**")
                sem2_modules = [m for m in modules if m['semestre'] == 2]
                if sem2_modules:
                    for m in sem2_modules:
                        st.write(f"- {m['nom']} ({m['credits']} credits)")
                else:
                    st.info("No modules")
            
            total_credits = sum(m['credits'] for m in modules)
            st.markdown(f"**Total Credits:** {total_credits}")
        else:
            st.info("No modules enrolled")
        
        st.markdown("---")
        
        # =====================================
        # EXAM SCHEDULE
        # =====================================
        
        st.subheader("📅 Your Exam Schedule")
        
        exams = get_student_exams(selected_student_id)
        
        if exams:
            # Check for conflicts
            conflicts = check_exam_conflicts(exams)
            
            if conflicts:
                st.error(f"⚠️ Warning: {len(conflicts)} scheduling conflict(s) detected!")
                for conf in conflicts:
                    st.warning(f"Conflict on {conf['date']} at {conf['time']}: {conf['module1']} and {conf['module2']}")
            else:
                st.success("✅ No scheduling conflicts detected")
            
            st.markdown("---")
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📝 Total Exams", len(exams))
            
            with col2:
                total_duration = sum(e['duree_minutes'] for e in exams)
                st.metric("⏱️ Total Hours", f"{total_duration / 60:.1f}")
            
            with col3:
                if exams:
                    first_exam = min(e['date_exam'] for e in exams)
                    last_exam = max(e['date_exam'] for e in exams)
                    exam_period = (last_exam - first_exam).days + 1
                    st.metric("📆 Exam Period", f"{exam_period} days")
            
            st.markdown("---")
            
            # Display mode selection
            display_mode = st.radio(
                "Display Mode:",
                ["Calendar View", "List View", "Table View"],
                horizontal=True
            )
            
            if display_mode == "Table View":
                df = pd.DataFrame(exams)
                df = df[['date_exam', 'heure_debut', 'module', 'salle', 'duree_minutes', 'professeur']]
                df.columns = ['Date', 'Time', 'Module', 'Room', 'Duration (min)', 'Professor']
                
                st.dataframe(df, use_container_width=True)
            
            elif display_mode == "List View":
                for exam in exams:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            st.markdown(f"### 📖 {exam['module']}")
                            st.markdown(f"👨‍🏫 Professor: {exam['professeur']}")
                        
                        with col2:
                            st.markdown(f"**📅 {exam['date_exam']}**")
                            st.markdown(f"**🕐 {exam['heure_debut']}**")
                            st.markdown(f"**⏱️ {exam['duree_minutes']} minutes**")
                        
                        with col3:
                            st.markdown(f"**🏛️ Room:**")
                            st.markdown(f"**{exam['salle']}**")
                        
                        st.markdown("---")
            
            else:  # Calendar View
                st.markdown("### 📆 Exam Calendar")
                
                # Group by date
                from collections import defaultdict
                exams_by_date = defaultdict(list)
                for exam in exams:
                    exams_by_date[exam['date_exam']].append(exam)
                
                for date in sorted(exams_by_date.keys()):
                    st.markdown(f"#### {date.strftime('%A, %B %d, %Y')}")
                    
                    for exam in exams_by_date[date]:
                        st.markdown(f"""
                        - **{exam['heure_debut']}** - {exam['module']} 
                          ({exam['duree_minutes']} min) in {exam['salle']}
                        """)
                    
                    st.markdown("")
            
            # =====================================
            # UPCOMING EXAMS
            # =====================================
            
            st.markdown("---")
            st.subheader("🔔 Upcoming Exams")
            
            today = datetime.now().date()
            week_later = today + timedelta(days=7)
            
            upcoming = [e for e in exams if today <= e['date_exam'] <= week_later]
            
            if upcoming:
                st.warning(f"⚠️ You have {len(upcoming)} exam(s) in the next 7 days!")
                
                for exam in upcoming:
                    days_until = (exam['date_exam'] - today).days
                    
                    if days_until == 0:
                        time_str = "TODAY"
                        color = "🔴"
                    elif days_until == 1:
                        time_str = "TOMORROW"
                        color = "🟠"
                    else:
                        time_str = f"in {days_until} days"
                        color = "🟡"
                    
                    st.markdown(f"""
                    {color} **{exam['module']}** - {time_str}
                    - Date: {exam['date_exam']}
                    - Time: {exam['heure_debut']}
                    - Room: {exam['salle']}
                    - Duration: {exam['duree_minutes']} minutes
                    """)
            else:
                st.success("✅ No exams in the next 7 days")
            
            # =====================================
            # DOWNLOAD SCHEDULE
            # =====================================
            
            st.markdown("---")
            st.subheader("📥 Download Your Schedule")
            
            df_export = pd.DataFrame(exams)
            df_export = df_export[['date_exam', 'heure_debut', 'module', 'salle', 'duree_minutes', 'professeur']]
            csv = df_export.to_csv(index=False)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv,
                    file_name=f"exam_schedule_{selected_student['matricule']}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        else:
            st.info("📭 No exams scheduled yet.")
            st.markdown("""
            **Possible reasons:**
            - The exam schedule hasn't been generated yet
            - You haven't enrolled in any modules
            - The exam period hasn't been configured
            
            Please contact your administrator or check back later.
            """)

except Exception as e:
    st.error(f"❌ Error loading student data: {str(e)}")
    st.exception(e)

# =====================================
# FOOTER
# =====================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Student Portal | Exam Planning System</p>
</div>
""", unsafe_allow_html=True)