import cv2
import face_recognition
import os
import datetime
import pandas as pd
import requests

# --- Configuration ---
KNOWN_FACES_DIR = "known_faces"
LOG_DIR = "attendance_logs"
os.makedirs(LOG_DIR, exist_ok=True)

API_ENDPOINT = "http://127.0.0.1:7860/update_attendance/"  # Optional API call (not required if local logging)
TOLERANCE = 0.45
MODEL = "hog"  # Use "cnn" if GPU available

# --- Load Known Faces ---
print("Loading known faces...")
known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if not os.path.isdir(person_dir):
        continue

    for filename in os.listdir(person_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            path = os.path.join(person_dir, filename)
            try:
                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_faces.append(encodings[0])
                    known_names.append(name)
            except Exception as e:
                print(f"Error loading {filename}: {e}")

print(f"Loaded {len(known_faces)} known faces successfully.")

# --- Initialize Camera ---
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("Error: Could not open camera.")
    exit()

print("\nStarting face recognition... (Press 'q' to quit)\n")

# --- Data Structures ---
logged_today = {}  # name -> date
recognized = False  # to close webcam automatically after success

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame, model=MODEL)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        name = "Unknown"
        matches = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)

        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]

            today = datetime.date.today().strftime("%Y-%m-%d")

            if logged_today.get(name) != today:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Optional: API call to FastAPI backend (not required for Excel)
                try:
                    response = requests.post(API_ENDPOINT + name)
                    if response.status_code == 200:
                        print(f"Attendance updated via API for {name}")
                except Exception:
                    pass  # Ignore API errors if local only

                logged_today[name] = today
                print(f"[{timestamp}] Access Granted: {name}")
                recognized = True

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

    cv2.imshow("Face Recognition Agent", frame)

    if recognized or (cv2.waitKey(5) & 0xFF == ord("q")):
        break

video_capture.release()
cv2.destroyAllWindows()
print("\nRecognition completed. Closing camera.")

# --- Generate Excel Report ---
if logged_today:
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    records = [
        {"Login Candidates": name, "Login Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for name in logged_today.keys()
    ]

    df_new = pd.DataFrame(records)
    excel_path = os.path.join(LOG_DIR, f"access_summary_{today_str}.xlsx")

    if os.path.exists(excel_path):
        df_existing = pd.read_excel(excel_path)
        combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=["Login Candidates"], keep="last")
        combined.to_excel(excel_path, index=False)
    else:
        df_new.to_excel(excel_path, index=False)

    print(f"Attendance summary saved to: {excel_path}")
else:
    print("No new attendance records found.")
