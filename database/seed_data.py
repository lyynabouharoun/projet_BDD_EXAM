import psycopg2
import random
from datetime import date

# -------------------------
# DATABASE CONNECTION
# -------------------------
conn = psycopg2.connect(
    dbname="exam_planning",
    user="postgres",
    password="lyna2003",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

print("Connected to database")

# -------------------------
# PARAMETERS (TUNABLE)
# -------------------------
NB_STUDENTS = 13000
NB_PROFESSORS = 120
MODULES_PER_FORMATION = 6
STUDENTS_PER_FORMATION = 250

# -------------------------
# DEPARTMENTS
# -------------------------
departements = [
    "Informatique",
    "Mathématiques",
    "Physique",
    "Chimie",
    "Biologie",
    "Agronomie",
    "STAPS"
]

cur.execute("DELETE FROM inscriptions")
cur.execute("DELETE FROM etudiants")
cur.execute("DELETE FROM modules")
cur.execute("DELETE FROM formations")
cur.execute("DELETE FROM professeurs")
cur.execute("DELETE FROM salles")
cur.execute("DELETE FROM batiments")
cur.execute("DELETE FROM departements")

for d in departements:
    cur.execute("INSERT INTO departements (nom) VALUES (%s)", (d,))

conn.commit()
print("Departments inserted")

# -------------------------
# FORMATIONS (LICENCE, MASTER, INGENIEUR)
# -------------------------
formations = []

cycles = [
    ("LICENCE", [1,2,3]),
    ("MASTER", [1,2]),
    ("INGENIEUR", [1,2,3,4])
]

for dept_id in range(1,8):
    for cycle, niveaux in cycles:
        for niv in niveaux:
            name = f"{cycle}_{niv}_D{dept_id}"
            cur.execute("""
                INSERT INTO formations (nom, cycle, niveau, departement_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, cycle, niv, dept_id))
            formations.append(cur.fetchone()[0])

conn.commit()
print(f"{len(formations)} formations inserted")

# -------------------------
# MODULES
# -------------------------
module_ids = []

for f_id in formations:
    for i in range(1, MODULES_PER_FORMATION + 1):
        cur.execute("""
            INSERT INTO modules (nom, formation_id, semestre, credits)
            VALUES (%s, %s, %s, 3)
            RETURNING id
        """, (f"Module_{i}_F{f_id}", f_id, random.choice([1,2])))
        module_ids.append(cur.fetchone()[0])

conn.commit()
print(f"{len(module_ids)} modules inserted")

# -------------------------
# PROFESSORS
# -------------------------
for i in range(NB_PROFESSORS):
    cur.execute("""
        INSERT INTO professeurs (nom, specialite, departement_id)
        VALUES (%s, %s, %s)
    """, (f"Prof_{i}", "Science", random.randint(1,7)))

conn.commit()
print("Professors inserted")

# -------------------------
# BUILDINGS & ROOMS
# -------------------------
cur.execute("INSERT INTO batiments (nom) VALUES ('Bloc A'),('Bloc B'),('Bloc C')")

for i in range(1,61):
    cur.execute("""
        INSERT INTO salles (nom, capacite, type, batiment_id)
        VALUES (%s, %s, %s, %s)
    """, (f"Salle_{i}", random.choice([20,30,100,300]), 
          "AMPHI" if i % 10 == 0 else "SALLE",
          random.randint(1,3)))

conn.commit()
print("Rooms inserted")

# -------------------------
# STUDENTS + INSCRIPTIONS
# -------------------------
student_count = 0
inscription_count = 0

for f_id in formations:
    for i in range(STUDENTS_PER_FORMATION):
        student_count += 1
        cur.execute("""
            INSERT INTO etudiants (matricule, nom, formation_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (f"MAT{student_count:06}", f"Etudiant_{student_count}", f_id))
        etudiant_id = cur.fetchone()[0]

        # inscriptions (6 modules per student)
        cur.execute("SELECT id FROM modules WHERE formation_id = %s", (f_id,))
        mods = [m[0] for m in cur.fetchall()]
        chosen = random.sample(mods, MODULES_PER_FORMATION)

        for m in chosen:
            cur.execute("""
                INSERT INTO inscriptions (etudiant_id, module_id)
                VALUES (%s, %s)
            """, (etudiant_id, m))
            inscription_count += 1

conn.commit()

print(f"Students inserted: {student_count}")
print(f"Inscriptions inserted: {inscription_count}")

cur.close()
conn.close()

print("DATASET GENERATION COMPLETED SUCCESSFULLY")
