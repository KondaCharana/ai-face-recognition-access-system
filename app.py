import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Access Control Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
        .main-title {
            font-size: 36px;
            font-weight: 700;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 15px;
        }

        .subheader {
            font-size: 22px;
            color: #374151;
            font-weight: 600;
            margin-top: 25px;
            margin-bottom: 10px;
        }

        .metric-card {
            background-color: #F9FAFB;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.08);
            text-align: center;
        }

        .metric-value {
            font-size: 30px;
            font-weight: 700;
            color: #111827;
        }

        .metric-label {
            font-size: 15px;
            color: #6B7280;
            margin-top: -5px;
        }

        div.stButton > button {
            background-color: #2563EB;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            transition: 0.2s;
        }

        div.stButton > button:hover {
            background-color: #1E40AF;
            transform: scale(1.02);
        }

        .footer {
            font-size: 13px;
            color: #6B7280;
            text-align: center;
            margin-top: 40px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="main-title">AI Access Control Dashboard</div>', unsafe_allow_html=True)
st.divider()

# --- Paths ---
LOG_DIR = "attendance_logs"
KNOWN_FACES_DIR = "known_faces"
today = datetime.today().strftime("%Y-%m-%d")
excel_path = os.path.join(LOG_DIR, f"access_summary_{today}.xlsx")

# --- Sidebar Navigation ---
menu = st.sidebar.radio(
    "Navigation",
    ["Live Recognition", "Register New User", "Daily Report"],
    index=2
)

# --- Summary Dashboard Section ---
st.markdown('<div class="subheader">Daily Summary</div>', unsafe_allow_html=True)

# --- Compute Stats ---
total_registered = len([d for d in os.listdir(KNOWN_FACES_DIR) if os.path.isdir(os.path.join(KNOWN_FACES_DIR, d))])
present_today = 0
absent_today = total_registered

if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    present_today = len(df["Login Candidates"].unique())
    absent_today = total_registered - present_today if total_registered > 0 else 0
else:
    df = pd.DataFrame(columns=["Login Candidates", "Login Time"])

# --- Display Metrics in 3 Columns ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_registered}</div>
            <div class="metric-label">Total Employees</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#059669;">{present_today}</div>
            <div class="metric-label">Present Today</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#DC2626;">{absent_today}</div>
            <div class="metric-label">Absent Today</div>
        </div>
    """, unsafe_allow_html=True)

# --- Page Logic ---
if menu == "Live Recognition":
    st.markdown('<div class="subheader">Live Face Recognition</div>', unsafe_allow_html=True)
    st.info("Click below to start recognition via webcam. The camera will close automatically after detection.")
    if st.button("Start Live Recognition"):
        os.system("python local_face_agent.py")
        st.success("Recognition session completed successfully.")

elif menu == "Register New User":
    st.markdown('<div class="subheader">Register New Employee</div>', unsafe_allow_html=True)
    name = st.text_input("Enter Employee Name:")

    st.write("Choose registration method:")
    option = st.radio(
        "Select Method",
        ["Upload Image", "Capture from Webcam"],
        horizontal=True
    )

    uploaded_file = None
    captured_image = None

    if option == "Upload Image":
        uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    else:
        captured_image = st.camera_input("Capture image using webcam")

    if st.button("Register"):
        if not name:
            st.error("Please enter the employee name.")
        else:
            save_dir = os.path.join(KNOWN_FACES_DIR, name)
            os.makedirs(save_dir, exist_ok=True)

            if option == "Upload Image" and uploaded_file:
                file_path = os.path.join(save_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                st.success(f"{name} successfully registered from uploaded image.")

            elif option == "Capture from Webcam" and captured_image:
                file_path = os.path.join(save_dir, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                with open(file_path, "wb") as f:
                    f.write(captured_image.getbuffer())
                st.success(f"{name} successfully registered using webcam capture.")

            else:
                st.error("Please provide an image (either upload or capture).")

elif menu == "Daily Report":
    st.markdown(f'<div class="subheader">Attendance Report — {today}</div>', unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True)

        with open(excel_path, "rb") as file:
            st.download_button(
                label="Download Today's Report (Excel)",
                data=file,
                file_name=f"access_summary_{today}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.warning("No attendance records found for today.")

# --- Footer ---
st.markdown('<div class="footer">Developed by Konda Charana | AI Access Control System</div>', unsafe_allow_html=True)
