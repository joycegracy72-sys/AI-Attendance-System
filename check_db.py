import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()

cur.execute("PRAGMA table_info(students)")
columns = cur.fetchall()

print("\nStudents Table Structure:\n")
for col in columns:
    print(f"Column: {col[1]} | Type: {col[2]}")

conn.close()