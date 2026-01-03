import psycopg2
from psycopg2.extras import RealDictCursor
from backend.config import DB_CONFIG


# =====================================
# DATABASE CONNECTION
# =====================================

def get_connection():
    """
    Creates and returns a new PostgreSQL connection
    """
    return psycopg2.connect(
        dbname=DB_CONFIG["dbname"],       # was DB_CONFIG["exam_planning"]
        user=DB_CONFIG["user"],           # was DB_CONFIG["postgres"]
        password=DB_CONFIG["password"],   # was DB_CONFIG["lyna2003"]
        host=DB_CONFIG["host"],           # was DB_CONFIG["localhost"]
        port=DB_CONFIG["port"]            # was DB_CONFIG["5432"]
    )

# =====================================
# FETCH FUNCTIONS
# =====================================

def fetch_formations():
    """
    Returns all formations
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM formations;")
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data


def fetch_modules_by_formation(formation_id):
    """
    Returns modules of a given formation
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM modules
        WHERE formation_id = %s
    """, (formation_id,))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def fetch_students_by_formation(formation_id):
    """
    Returns students enrolled in a formation
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM etudiants
        WHERE formation_id = %s
    """, (formation_id,))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def fetch_professors():
    """
    Returns all professors
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM professeurs;")
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data


def fetch_rooms():
    """
    Returns all rooms
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM salles;")
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data


# =====================================
# EXAMS MANAGEMENT
# =====================================

def clear_existing_exams():
    """
    Deletes all exams before regeneration
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM examens;")
    conn.commit()

    cur.close()
    conn.close()


def insert_exam(module_id, prof_id, salle_id, date_exam, heure_debut, duree):
    """
    Inserts a single exam into database
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO examens
        (module_id, prof_id, salle_id, date_exam, heure_debut, duree_minutes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (module_id, prof_id, salle_id, date_exam, heure_debut, duree))

    conn.commit()
    cur.close()
    conn.close()


def fetch_all_exams():
    """
    Returns all scheduled exams
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT e.id, m.nom AS module, s.nom AS salle,
               e.date_exam, e.heure_debut, e.duree_minutes
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN salles s ON e.salle_id = s.id
        ORDER BY e.date_exam, e.heure_debut
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data
