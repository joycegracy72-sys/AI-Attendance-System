# ==============================
# Smart Attendance - MAIN FILE
# Saves attendance to Excel + SQLite
# ==============================

import cv2
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ---------- Load Face Model ----------
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face_trained.yml")

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# ---------- Load Labels ----------
label_map = {}
with open("labels.txt", "r") as f:
    for line in f:
        k, v = line.strip().split(",")
        label_map[int(k)] = v.strip()

# ---------- Database ----------
DB_PATH = "students.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ---------- Excel Attendance File ----------
today_date = datetime.now().strftime("%Y-%m-%d")
attendance_dir = "attendance"
os.makedirs(attendance_dir, exist_ok=True)
attendance_file = f"{attendance_dir}/{today_date}.xlsx"

if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=["Name", "RegNo", "Department", "Time"])
    df.to_excel(attendance_file, index=False)

# ---------- Camera ----------
cap = cv2.VideoCapture(0)
attendance_marked = False

print("Camera started... Press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        id_, conf = recognizer.predict(face)

        color = (0, 0, 255)
        status_text = "Unknown Face"

        if conf < 60 and id_ in label_map:
            full_label = label_map[id_].strip()   # e.g. Joyce_1038
            reg_no = full_label.split("_")[-1]

            cur.execute("""
                SELECT id, name, reg_no, dept
                FROM students
                WHERE TRIM(reg_no) = TRIM(?)
            """, (reg_no,))
            row = cur.fetchone()

            if row:
                student_id, name, reg_no_db, dept = row

                df = pd.read_excel(attendance_file)

                # Check duplicate in Excel
                if str(reg_no_db) in df["RegNo"].astype(str).values:
                    status_text = "Attendance already marked"
                    color = (0, 255, 255)

                else:
                    now = datetime.now().strftime("%H:%M:%S")

                    # ===== SAVE TO EXCEL =====
                    df.loc[len(df)] = [name, reg_no_db, dept, now]
                    df.to_excel(attendance_file, index=False)

                    # ===== SAVE TO SQLITE =====
                    cur.execute("""
                        INSERT INTO attendance (student_id, date, time, status)
                        VALUES (?, ?, ?, ?)
                    """, (student_id, today_date, now, "Present"))
                    conn.commit()

                    status_text = "Attendance marked"
                    color = (0, 255, 0)
                    attendance_marked = True
            else:
                status_text = "Student not found"
                color = (0, 165, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, status_text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Smart Attendance", frame)

    if attendance_marked:
        cv2.waitKey(2000)
        break

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()

print("Attendance process completed.")