import psycopg2
from psycopg2.extras import RealDictCursor
from backend.config import DB_CONFIG
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )

# =====================================
# LOGIN FUNCTIONS (PLAIN PASSWORD - TESTING)
# =====================================

def validate_staff_login(email, password):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT 
            id,
            nom,
            prenom,
            role,
            departement_id
        FROM staff
        WHERE email = %s AND password = %s
    """, (email, password))

    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

# ---------- STUDENT LOGIN ----------

def validate_student_login(matricule, date_naissance):
    """
    Student login using matricule + date_naissance (YYYY-MM-DD)
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, nom, prenom, formation_id
        FROM etudiants
        WHERE matricule = %s
          AND date_naissance = %s
    """, (matricule, date_naissance))

    student = cur.fetchone()
    cur.close()
    conn.close()
    return student

# ---------- PROFESSOR LOGIN ----------

def validate_prof_login(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nom, prenom, departement_id
        FROM professeurs
        WHERE email = %s AND password = %s
    """, (email, password))

    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nom": row[1],
            "prenom": row[2],
            "departement_id": row[3],
            "role": "prof"
        }

    return None


# ---------- EXAM FETCH ----------
def fetch_student_schedule(student_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT
    ex.id,
    m.nom AS module,
    f.nom AS formation,
    s.nom AS salle,
    ex.date_exam,
    ex.heure_debut,
    ex.duree_minutes
FROM exam_groups eg
JOIN examens ex ON eg.exam_id = ex.id
JOIN modules m ON ex.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN salles s ON ex.salle_id = s.salle_id
WHERE eg.student_id = %s
ORDER BY ex.date_exam, ex.heure_debut;

    """, (student_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_prof_schedule(prof_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT e.id, m.nom AS module, f.nom AS formation, s.nom AS salle, e.date_exam, e.heure_debut, e.duree_minutes
        FROM examens e
        JOIN modules m ON e.module_id=m.id
        JOIN formations f ON m.formation_id=f.id
        JOIN salles s ON e.salle_id=s.salle_id
        WHERE e.prof_id=%s
        ORDER BY e.date_exam, e.heure_debut
    """, (prof_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_department_schedule(department_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT e.id AS exam_id, m.nom AS module_name, f.nom AS formation_name, f.id AS formation_id,
               f.departement_id, f.approved AS formation_approved,
               s.nom AS room_name, s.capacite AS room_capacity,
               p.nom || ' ' || p.prenom AS professor_name,
               e.date_exam, e.heure_debut, e.duree_minutes
        FROM examens e
        JOIN modules m ON e.module_id=m.id
        JOIN formations f ON m.formation_id=f.id
        JOIN salles s ON e.salle_id=s.salle_id
        JOIN professeurs p ON e.prof_id=p.id
        WHERE f.departement_id=%s
        ORDER BY e.date_exam, e.heure_debut
    """, (department_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def approve_department_schedule(department_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE formations SET approved=TRUE WHERE departement_id=%s", (department_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True

def fetch_all_departments_schedule():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT e.id AS exam_id, m.nom AS module_name, f.nom AS formation_name,
               f.departement_id, s.nom AS room_name, p.nom || ' ' || p.prenom AS professor_name,
               e.date_exam, e.heure_debut, e.duree_minutes, f.approved AS formation_approved
        FROM examens e
        JOIN modules m ON e.module_id=m.id
        JOIN formations f ON m.formation_id=f.id
        JOIN salles s ON e.salle_id=s.salle_id
        JOIN professeurs p ON e.prof_id=p.id
        ORDER BY f.departement_id, e.date_exam, e.heure_debut
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def approve_final_schedule():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE formations SET approved=TRUE")
    conn.commit()
    cur.close()
    conn.close()
    return True

#---------- FETCH FORMATIONS ----------

def fetch_formations():
    """Return all formations from the database"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM formations ORDER BY nom")
    formations = cur.fetchall()
    cur.close()
    conn.close()
    return formations


# Optional admin dashboard
def fetch_admin_dashboard_data():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT s.nom AS salle, COUNT(e.id) AS nb_examens, SUM(s.capacite) AS total_capacity
        FROM salles s
        LEFT JOIN examens e ON s.salle_id=e.salle_id
        GROUP BY s.nom
        ORDER BY nb_examens DESC
    """)
    rooms = cur.fetchall()
    cur.execute("""
        SELECT p.nom || ' ' || p.prenom AS professeur, COUNT(e.id) AS nb_examens
        FROM professeurs p
        LEFT JOIN examens e ON p.id=e.prof_id
        GROUP BY p.id
        ORDER BY nb_examens DESC
    """)
    professors = cur.fetchall()
    cur.execute("""
        SELECT st.nom || ' ' || st.prenom AS student, e1.date_exam, e1.heure_debut, COUNT(*) AS nb_conflicts
        FROM inscriptions i1
        JOIN examens e1 ON i1.module_id=e1.module_id
        JOIN inscriptions i2 ON i1.etudiant_id=i2.etudiant_id
        JOIN examens e2 ON i2.module_id=e2.module_id
        JOIN etudiants st ON i1.etudiant_id=st.id
        WHERE e1.id<>e2.id AND e1.date_exam=e2.date_exam AND e1.heure_debut=e2.heure_debut
        GROUP BY st.id, e1.date_exam, e1.heure_debut
        HAVING COUNT(*)>1
        ORDER BY nb_conflicts DESC
    """)
    student_conflicts = cur.fetchall()
    cur.close()
    conn.close()
    return {"rooms": rooms, "professors": professors, "student_conflicts": student_conflicts}


def clear_existing_exams():
    """
    Delete all existing exams before regenerating a new schedule
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM examens;")
    conn.commit()
    cur.close()
    conn.close()

#---------- FETCH MODULES AND STUDENTS BY FORMATION ----------

def fetch_modules_by_formation(formation_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    m.id,
                    m.nom,
                    f.departement_id
                FROM modules m
                JOIN formations f ON m.formation_id = f.id
                WHERE m.formation_id = %s
            """, (formation_id,))
            return cur.fetchall()

def fetch_students_by_formation(formation_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM etudiants WHERE formation_id=%s", (formation_id,))
    students = cur.fetchall()
    cur.close()
    conn.close()
    return students

def fetch_rooms():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT salle_id, nom, capacite FROM salles")  # id here
    rooms = cur.fetchall()
    cur.close()
    conn.close()
    return rooms

def fetch_professors():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM professeurs ORDER BY nom")
    professors = cur.fetchall()
    cur.close()
    conn.close()
    return professors

# ---------- INSERT EXAM ----------


def insert_exam(module_id, salle_id, prof_id, date_exam, heure_debut, duree_minutes, conn=None, commit=True):
    if conn is None:
        conn = get_connection()
        close_after = True
    else:
        close_after = False

    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO examens (module_id, salle_id, prof_id, date_exam, heure_debut, duree_minutes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (module_id, salle_id, prof_id, date_exam, heure_debut, duree_minutes))
        
        exam_id = cur.fetchone()[0]     # get the generated id
        if commit:
            conn.commit()
        # Removed print for performance
        return exam_id                  # ← return integer id, not True

    except psycopg2.errors.UniqueViolation:
        if commit:
            conn.rollback()
        return None                     # or raise, depending on your logic

    except Exception as e:
        if commit:
            conn.rollback()
        raise e

    finally:
        cur.close()
        if close_after:
            conn.close()


def insert_exam_groups(exam_id, student_ids, conn=None, commit=True):
    if conn is None:
        conn = get_connection()
        close_after = True
    else:
        close_after = False

    cur = conn.cursor()
    try:
        cur.executemany("""
            INSERT INTO exam_groups (exam_id, student_id)
            VALUES (%s, %s)
        """, [(exam_id, sid) for sid in student_ids])
        if commit:
            conn.commit()
        # Removed print for performance

    except Exception as e:
        if commit:
            conn.rollback()
        raise e

    finally:
        cur.close()
        if close_after:
            conn.close()
