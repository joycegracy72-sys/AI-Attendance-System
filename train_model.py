import cv2
import os
import numpy as np

DATASET_PATH = "dataset"
MODEL_PATH = "face_trained.yml"

faces = []
labels = []
label_map = {}   # numeric_id -> folder_name
current_id = 0

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Walk through each student folder
for folder in os.listdir(DATASET_PATH):
    folder_path = os.path.join(DATASET_PATH, folder)
    if not os.path.isdir(folder_path):
        continue

    label_map[current_id] = folder

    for img_name in os.listdir(folder_path):
        img_path = os.path.join(folder_path, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        faces.append(img)
        labels.append(current_id)

    current_id += 1

if len(faces) == 0:
    print("No training images found.")
    exit()

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(labels))
recognizer.save(MODEL_PATH)

# Save label map
with open("labels.txt", "w") as f:
    for k, v in label_map.items():
        f.write(f"{k},{v}\n")

print("Model trained successfully.")
print(f"Students trained: {len(label_map)}")
print(f"Images used: {len(faces)}")