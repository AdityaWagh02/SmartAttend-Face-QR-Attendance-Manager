# 📸 SmartAttend - Face + QR Code Attendance Management System

A robust **real-time attendance system** using **Face Recognition + QR Code** verification, developed with Python, OpenCV, Dlib, face\_recognition, and MySQL.

---

## 🚀 Features

- 👤 **Register Students** with personal info
- 📷 **Capture Face Image** using webcam
- 📎 **Generate QR Code** containing student ID and name
- 🤖 **Dual-Layer Attendance Verification**
  - Face recognition
  - QR code scanning
- 🧠 Uses `face_recognition` for identifying known faces
- 🛡️ **Prevents spoofing** with QR + Face match
- 🗃️ **Data persistence** with MySQL

---

## 🧰 Tech Stack

| Tech                     | Use                          |
| ------------------------ | ---------------------------- |
| Python                   | Core application logic       |
| OpenCV                   | Webcam and image processing  |
| Dlib / face\_recognition | Face encoding & recognition  |
| MySQL                    | Student and attendance data  |
| QRCode                   | QR generation & verification |

---

## 🗃️ Database Setup

Create a database named `attendance` and execute the following SQL:

```sql
CREATE DATABASE attendance;
USE attendance;

CREATE TABLE students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  age INT,
  gender VARCHAR(10),
  email VARCHAR(100)
);

CREATE TABLE attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  date DATE,
  in_time TIME,
  FOREIGN KEY (student_id) REFERENCES students(student_id)
);
```

> 💡 Default MySQL port is set to `3300`. Change in code if using `3306`.

---

## 🔧 Configuration

- Update the following in your code as per your system:

```python
image_dir = r"F:\\Attendance ManagmentSystem\\Face_Rcognization"
qr_code_dir = r"F:\\Attendance ManagmentSystem\\QR_code"
```

- Set MySQL credentials:

```python
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="attendance",
    port=3300
)
```

---

## ▶️ Running the Application

1. Ensure MySQL server is running
2. Python 3.7+ recommended
3. Install required libraries:

```bash
pip install opencv-python dlib face_recognition mysql-connector-python qrcode numpy
```

4. Run the script:

```bash
python main.py
```

5. Use the interactive console:

```
--- Attendance Management System ---
1. Register Student and Capture Image
2. Take Attendance
3. Exit
```

---

## 🧪 Example Flow

1. Register student: Name, Age, Gender, Email
2. Image is captured & saved
3. QR code is generated and saved
4. For attendance:
   - Face is matched with existing data
   - QR code is scanned
   - Attendance is marked only if both match

---

## 💡 Future Improvements

- ✅ GUI (Tkinter/Flask)
- ✅ Add Admin login & dashboards
- ✅ Export attendance as CSV/PDF
- ✅ Email alerts or SMS integration
- ✅ Cloud database integration

---

## 🧠 Best Practices

- Use good lighting when capturing images
- Ensure only one face in camera during capture
- Keep dataset images clear and front-facing
- Don’t forget to shut down MySQL server properly

---

> This system is ideal for college, coaching, or office use. Lightweight, offline-capable, and secure.

---

Feel free to fork, improve, or suggest changes!

