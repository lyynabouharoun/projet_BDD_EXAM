import psycopg2

# -------------------------
# DATABASE CONNECTION
# -------------------------
conn = psycopg2.connect(
    dbname="exam_planning",
    user="postgres",
    password="lyna2003",   # <-- replace
    host="localhost",
    port="5432"
)

cur = conn.cursor()

print("\n===== DATABASE CONTENT CHECK =====\n")

tables = [
    "departements",
    "formations",
    "modules",
    "professeurs",
    "etudiants",
    "inscriptions",
    "salles",
    "examens"
]

for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    print(f"{table:<15} : {count}")

# -------------------------
# ADDITIONAL SANITY CHECKS
# -------------------------

# Students per cycle
cur.execute("""
SELECT cycle, COUNT(e.id)
FROM etudiants e
JOIN formations f ON e.formation_id = f.id
GROUP BY cycle;
""")

print("\nStudents per cycle:")
for row in cur.fetchall():
    print(row)

# Modules per formation
cur.execute("""
SELECT formation_id, COUNT(*)
FROM modules
GROUP BY formation_id
LIMIT 5;
""")

print("\nSample modules per formation:")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()

print("\nDATABASE CHECK COMPLETED SUCCESSFULLY")
