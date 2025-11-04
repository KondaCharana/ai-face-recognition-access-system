# 🤖 AI Access Control Agent — Face Recognition Attendance System

An intelligent **AI-based facial recognition attendance and access control system**, developed using **Python, OpenCV, Streamlit, and FastAPI**.  
It automates employee identification, attendance logging, and daily reporting with real-time recognition.

---

## Project Overview

This project detects faces using a webcam, matches them with stored encodings, and automatically logs attendance into a daily Excel report.  
Managers can view attendance through a modern Streamlit dashboard, register new employees, or monitor daily reports.

---

## Tech Stack

- **Python 3.9+**
- **Streamlit** — Interactive Dashboard UI
- **OpenCV** — Real-time camera access
- **face_recognition** — Deep Learning-based face detection
- **FastAPI** — Backend API for data logging
- **Pandas / Excel Writer** — Attendance report generation

---

## ⚙️ Features

✅ Real-time Face Recognition  
✅ Auto Attendance Logging  
✅ Streamlit Dashboard for Monitoring  
✅ Daily Excel Summary Reports  
✅ Employee Registration via Upload or Webcam  
✅ API Endpoint Integration (for dashboards or cloud systems)

---

## 📂 Project Structure

ai-access-agent/
├── app.py # Streamlit dashboard
├── api_server.py # FastAPI backend for attendance
├── local_face_agent.py # Core recognition agent
├── known_faces/ # Folder with registered employee images
├── attendance_logs/ # Daily generated Excel reports
├── requirements.txt # Dependencies
└── README.md # Project documentation

---

## 🚀 Getting Started (Local Setup)

### 1️⃣ Clone this Repository

git clone https://github.com/yourusername/ai-access-agent.git
cd ai-access-agent

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Run the Dashboard
streamlit run app.py

4️⃣ (Optional) Run API Server
uvicorn api_server:app --reload

API Endpoints (FastAPI)
Endpoint Method Description
/update_attendance/{name} POST Updates attendance for recognized employee
/get_report GET Fetches daily attendance report in Excel format

### Sample Workflow

Register Employee – Upload face image or capture via webcam.

Run Live Recognition – Automatically detects and logs attendance.

View Daily Report – Dashboard shows present and absent employees.

Download Excel File – Click "Download Today's Report" for manager view.

### Future Enhancements

🔐 Google Cloud / Hugging Face Deployment

📸 Pi Camera Integration for IoT Hardware

🧠 OCR-based Employee ID Reader

☁️ GCP Pub/Sub for cloud clustering

🤝 Integration with company CRM or Slack Alerts

🧑‍💻 Developed By

Konda Charana
AI/ML Developer | Automation Engineer | AI Integrations
📍 Hyderabad, India

🔗 LinkedIn : https://www.linkedin.com/in/konda-charana-1010a6190/

📧 Email: kondacharana@gmail.com
