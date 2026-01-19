import psycopg2
import random
from datetime import date, timedelta
from faker import Faker
import hashlib

fake = Faker()

# -------------------------
# DATABASE CONNECTION
# -------------------------
conn = psycopg2.connect(
    dbname="num_exam",
    user="postgres",
    password="lyna2003",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
print("Connected to database")

# -------------------------
# PARAMETERS
# -------------------------
NB_STUDENTS = 13000
NB_PROFESSORS = 120
MODULES_MIN = 6
MODULES_MAX = 9
STUDENTS_PER_FORMATION = None  # will distribute evenly later
NB_STAFF = 20  # admin, doyen, vice-doyen, chef-departements
NB_BUILDINGS = 3
NB_ROOMS = 60
DEPARTMENTS = [
    "Informatique",
    "Mathématiques",
    "Physique",
    "Chimie",
    "Biologie",
    "Agronomie",
    "STAPS"
]
CYCLES = [
    ("LICENCE", [1,2,3]),
    ("MASTER", [1,2]),
    ("INGENIEUR", [1,2,3,4,5])
]

# -------------------------
# CLEAR EXISTING DATA
# -------------------------
tables = ["inscriptions","etudiant_logins","etudiants","modules","formations","professeurs","staff","salles","batiments","departements"]
for t in tables:
    cur.execute(f"DELETE FROM {t}")

conn.commit()
print("Existing data cleared")

# -------------------------
# DEPARTMENTS
# -------------------------
for d in DEPARTMENTS:
    cur.execute("INSERT INTO departements (nom) VALUES (%s)", (d,))
conn.commit()
print("Departments inserted")

# -------------------------
# FORMATIONS
# -------------------------
formations = []
for dept_id in range(1, len(DEPARTMENTS)+1):
    for cycle, niveaux in CYCLES:
        for niv in niveaux:
            # 1-2 formations per level to match ~200 total
            num_formations = random.randint(1,2)
            for f_idx in range(num_formations):
                name = f"{cycle}_{niv}_F{dept_id}_{f_idx+1}"
                cur.execute("""
                    INSERT INTO formations (nom, cycle, niveau, departement_id)
                    VALUES (%s,%s,%s,%s) RETURNING id
                """, (name, cycle, niv, dept_id))
                formations.append(cur.fetchone()[0])
conn.commit()
print(f"{len(formations)} formations inserted")

# -------------------------
# MODULES
# -------------------------
module_ids = []
for f_id in formations:
    nb_modules = random.randint(MODULES_MIN, MODULES_MAX)
    for i in range(1, nb_modules+1):
        cur.execute("""
            INSERT INTO modules (nom, formation_id, semestre, credits)
            VALUES (%s,%s,%s,3) RETURNING id
        """, (f"Module_{i}_F{f_id}", f_id, random.choice([1,2])))
        module_ids.append(cur.fetchone()[0])
conn.commit()
print(f"{len(module_ids)} modules inserted")

# -------------------------
# PROFESSORS
# -------------------------
for i in range(NB_PROFESSORS):
    cur.execute("""
        INSERT INTO professeurs (nom, prenom, specialite, departement_id)
        VALUES (%s,%s,%s,%s)
    """, (fake.last_name(), fake.first_name(), "Science", random.randint(1,len(DEPARTMENTS))))
conn.commit()
print(f"{NB_PROFESSORS} professors inserted")

# -------------------------
# STAFF USERS
# -------------------------
roles = ["ADMIN","DOYEN","VICE_DOYEN","CHEF_DEPARTEMENT"]
for i in range(NB_STAFF):
    email = fake.email()
    password = "password123"  # default fake password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    role = random.choice(roles)
    dept_id = random.randint(1,len(DEPARTMENTS)) if role in ["CHEF_DEPARTEMENT"] else None
    cur.execute("""
        INSERT INTO staff (nom, prenom, email, password_hash, role, departement_id)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (fake.last_name(), fake.first_name(), email, password_hash, role, dept_id))
conn.commit()
print(f"{NB_STAFF} staff users inserted")

# -------------------------
# BUILDINGS & ROOMS
# -------------------------
for i in range(1, NB_BUILDINGS+1):
    cur.execute("INSERT INTO batiments (nom) VALUES (%s)", (f"Bloc {chr(64+i)}",))

for i in range(1, NB_ROOMS+1):
    cur.execute("""
        INSERT INTO salles (nom, capacite, type, batiment_id)
        VALUES (%s,%s,%s,%s)
    """, (
        f"Salle_{i}",
        random.choice([20,30,100,300]),
        "AMPHI" if i%10==0 else "SALLE",
        random.randint(1,NB_BUILDINGS)
    ))
conn.commit()
print(f"{NB_BUILDINGS} buildings and {NB_ROOMS} rooms inserted")

# -------------------------
# STUDENTS + LOGINS + INSCRIPTIONS
# -------------------------
student_count = 0
inscription_count = 0
students_per_formation = NB_STUDENTS // len(formations)

for f_id in formations:
    for i in range(students_per_formation):
        student_count +=1
        nom = fake.last_name()
        prenom = fake.first_name()
        # Random birthday between 18 and 25 years old
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=25)
        matricule = f"MAT{student_count:06}"
        # Insert student
        cur.execute("""
            INSERT INTO etudiants (matricule, nom, prenom, date_naissance, formation_id)
            VALUES (%s,%s,%s,%s,%s) RETURNING id
        """,(matricule, nom, prenom, birthday, f_id))
        etudiant_id = cur.fetchone()[0]

        # Student login password: hash(matricule + birthday)
        pwd_raw = f"{matricule}{birthday}"
        pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()
        cur.execute("""
            INSERT INTO etudiant_logins (etudiant_id, password_hash)
            VALUES (%s,%s)
        """,(etudiant_id, pwd_hash))

        # Inscriptions: all modules for formation (6–9)
        cur.execute("SELECT id FROM modules WHERE formation_id=%s", (f_id,))
        modules_for_f = [m[0] for m in cur.fetchall()]
        chosen_modules = random.sample(modules_for_f, min(len(modules_for_f), random.randint(MODULES_MIN,MODULES_MAX)))
        for m in chosen_modules:
            cur.execute("""
                INSERT INTO inscriptions (etudiant_id, module_id)
                VALUES (%s,%s)
            """,(etudiant_id, m))
            inscription_count +=1

conn.commit()
print(f"{student_count} students inserted with logins")
print(f"{inscription_count} inscriptions inserted")

cur.close()
conn.close()
print("DATASET GENERATION COMPLETED SUCCESSFULLY")
