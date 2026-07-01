import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()

print("\n=== Student Registration ===")
name = input("Enter Name: ").strip()
reg_no = input("Enter Register Number: ").strip()
dept = input("Enter Department: ").strip()

try:
    cur.execute(
        "INSERT INTO students (name, reg_no, dept) VALUES (?, ?, ?)",
        (name, reg_no, dept)
    )
    conn.commit()
    print("\nStudent registered successfully")
except sqlite3.IntegrityError:
    print("\nRegister number already exists")

conn.close()