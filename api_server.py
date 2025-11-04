from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
import cv2
import face_recognition
from datetime import datetime

app = FastAPI(title="Face Recognition Access Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "access_summary.xlsx"
KNOWN_FACES_DIR = "known_faces"

# Ensure directories exist
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Login Candidates", "Login Time"]).to_excel(DATA_FILE, index=False)

@app.get("/")
def home():
    return {"message": "API is running successfully"}

@app.get("/attendance")
def get_attendance():
    df = pd.read_excel(DATA_FILE)
    return df.to_dict(orient="records")

@app.post("/update_attendance/{name}")
def update_attendance(name: str):
    df = pd.read_excel(DATA_FILE)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {"Login Candidates": name, "Login Time": now}
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)
    return {"message": f"Attendance updated for {name}", "time": now}


# 🆕 NEW FEATURE — REGISTER NEW USER
@app.post("/register_user/{name}")
def register_user(name: str):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(person_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JSONResponse(content={"error": "Cannot access webcam"}, status_code=500)

    count = 0
    while count < 5:  # Capture 5 sample images
        ret, frame = cap.read()
        if not ret:
            continue
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if face_locations:
            count += 1
            filename = os.path.join(person_dir, f"{name}_{count}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Saved {filename}")
        cv2.imshow("Registering User", frame)
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return {"message": f"User {name} registered successfully with {count} images"}
