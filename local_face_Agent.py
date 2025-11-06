import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
from datetime import datetime
import streamlit as st

class LocalFaceAgent:
    def __init__(self):
        self.known_faces_dir = "known_faces"
        self.log_dir = "attendance_logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.excel_path = os.path.join(self.log_dir, f"access_summary_{self.today}.xlsx")

        self.known_encodings = []
        self.known_names = []
        self.load_known_faces()

    def load_known_faces(self):
        """Load and encode all registered faces."""
        for name in os.listdir(self.known_faces_dir):
            person_dir = os.path.join(self.known_faces_dir, name)
            if not os.path.isdir(person_dir):
                continue

            for img_file in os.listdir(person_dir):
                if img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                    image = face_recognition.load_image_file(os.path.join(person_dir, img_file))
                    encodings = face_recognition.face_encodings(image)
                    if len(encodings) > 0:
                        self.known_encodings.append(encodings[0])
                        self.known_names.append(name)

    def log_attendance(self, name):
        """Save attendance record."""
        now = datetime.now().strftime("%H:%M:%S")
        if os.path.exists(self.excel_path):
            df = pd.read_excel(self.excel_path)
        else:
            df = pd.DataFrame(columns=["Login Candidates", "Login Time"])

        if name not in df["Login Candidates"].values:
            new_row = pd.DataFrame([[name, now]], columns=["Login Candidates", "Login Time"])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(self.excel_path, index=False, engine="openpyxl")

    def start_recognition(self):
        """Run live recognition — Streamlit compatible."""
        stframe = st.empty()  # placeholder for displaying frames
        cap = cv2.VideoCapture(0)
        recognized = set()
        max_frames = 400
        frame_count = 0

        if not cap.isOpened():
            st.error("❌ Cannot access webcam. Please check camera permissions.")
            return

        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small)
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            for face_encoding, face_loc in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                name = "Unknown"

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_names[best_match_index]

                if name != "Unknown" and name not in recognized:
                    self.log_attendance(name)
                    recognized.add(name)

                top, right, bottom, left = [v * 4 for v in face_loc]
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # Convert BGR to RGB for Streamlit display
            stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

            frame_count += 1

        cap.release()

        if recognized:
            st.success(f"✅ Recognition complete — Detected: {', '.join(recognized)}")
        else:
            st.warning("⚠️ No known faces detected during this session.")
