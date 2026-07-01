import cv2
import sqlite3
import os

# Connect database
conn = sqlite3.connect("students.db")
cur = conn.cursor()

reg_no = input("Enter Register Number: ").strip()
cur.execute("SELECT id, name, dept FROM students WHERE reg_no = ?", (reg_no,))
row = cur.fetchone()

if row is None:
    print("Student not found. Register first.")
    conn.close()
    exit()

student_id, name, dept = row

# Create safe folder name
safe_name = "".join(c for c in name if c.isalnum())
folder_name = f"{safe_name}_{reg_no}"
user_folder = os.path.join("dataset", folder_name)
os.makedirs(user_folder, exist_ok=True)

print(f"\nManual capture for {name} ({reg_no} - {dept})")
print("Press 'C' to capture | Press 'Q' to quit")

# Face detector
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0)
count = len(os.listdir(user_folder))  # continue if already exists

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    face_detected = False
    face_img = None

    for (x, y, w, h) in faces:
        face_detected = True
        face_img = gray[y:y+h, x:x+w]

        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(frame, f"Samples: {count}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Manual Face Capture", frame)
    key = cv2.waitKey(1) & 0xFF

    # Capture on C
    if key == ord('c') and face_detected:
        count += 1
        file_path = os.path.join(user_folder, f"{count}.jpg")
        cv2.imwrite(file_path, face_img)
        print(f"Captured sample {count}")

    # Quit on Q
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()

print(f"\nDone. Total samples for {name}: {count}")