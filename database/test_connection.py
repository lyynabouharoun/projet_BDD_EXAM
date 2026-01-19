import psycopg2

conn = psycopg2.connect(
    dbname="num_exam",
    user="postgres",
    password="lyna2003",
    host="localhost",
    port="5432"
)

print("Connection OK")
conn.close()
