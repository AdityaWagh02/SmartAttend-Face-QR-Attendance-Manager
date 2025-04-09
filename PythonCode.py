import os

import cv2
import dlib
import face_recognition
import mysql.connector
import numpy
import qrcode

print("dlib version:", dlib.__version__)
print("Everything is working!")
print("MySQL connector is working!")

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="attendance",
    port=3300  # Change to 3306 if needed
)

cursor = conn.cursor()

# Path to store images and QR codes
image_dir = r"F:\Attendance ManagmentSystem\Face_Rcognization"
qr_code_dir = r"F:\Attendance ManagmentSystem\QR_code"

# Function to register a new student
def register_student():
    name = input("Enter student name: ")
    age = int(input("Enter student age: "))
    gender = input("Enter student gender: ")
    email = input("Enter student email: ")

    sql = "INSERT INTO students (name, age, gender, email) VALUES (%s, %s, %s, %s)"
    values = (name, age, gender, email)
    cursor.execute(sql, values)
    conn.commit()

    student_id = cursor.lastrowid
    print("Student registered successfully with ID:", student_id)
    generate_qr_code(student_id, name)
    return student_id

# Capture and store student image
def capture_image(student_id):
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Student Image")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Capture Student Image", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            img_name = f"{student_id}.jpg"
            cv2.imwrite(os.path.join(image_dir, img_name), frame)
            print(f"Image captured and saved as {img_name}")
            break

    cam.release()
    cv2.destroyAllWindows()

# Generate a QR code
def generate_qr_code(student_id, name):
    qr_data = f"ID: {student_id}, Name: {name}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    qr_code_path = os.path.join(qr_code_dir, f"{student_id}.png")
    img.save(qr_code_path)
    print(f"QR code generated and saved as {qr_code_path}")

# Generate QR codes for all students
def generate_qr_codes_for_all_students():
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()
    for student_id, student_name in students:
        generate_qr_code(student_id, student_name)

# Mark attendance with face + QR
def mark_attendance():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Student Image for Attendance")

    attendance_img = None
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Capture Student Image for Attendance", frame)

        k = cv2.waitKey(1)
        if k % 256 == 32:
            attendance_img = frame
            break

    cam.release()
    cv2.destroyAllWindows()

    if attendance_img is None:
        print("No image captured for attendance.")
        return

    # Load known faces
    known_face_encodings = []
    known_student_ids = []

    for file in os.listdir(image_dir):
        if not file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        img_path = os.path.join(image_dir, file)
        img = cv2.imread(img_path)

        if img is None:
            print(f"[ERROR] Failed to load image: {img_path}")
            continue

        # Convert to RGB for face recognition
        try:
            if len(img.shape) == 2:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            else:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"[ERROR] Could not convert image {img_path} to RGB: {e}")
            continue

        face_encodings = face_recognition.face_encodings(img_rgb)

        if face_encodings:
            known_face_encodings.append(face_encodings[0])
            student_id = os.path.splitext(file)[0]
            known_student_ids.append(student_id)
        else:
            print(f"[WARNING] No face found in image: {img_path}")

    # Detect face in captured image
    attendance_img_rgb = cv2.cvtColor(attendance_img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(attendance_img_rgb)
    face_encodings = face_recognition.face_encodings(attendance_img_rgb, face_locations)

    if not face_encodings:
        print("No faces detected in the captured image.")
        return

    matched_student_id = None
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = numpy.argmin(face_distances)

        if matches[best_match_index]:
            matched_student_id = known_student_ids[best_match_index]
            break

    if not matched_student_id:
        print("Face not recognized.")
        return

    # QR code scanning
    cap = cv2.VideoCapture(0)
    qr_detector = cv2.QRCodeDetector()
    scanned_qr = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        qr_data, bbox, _ = qr_detector.detectAndDecode(frame)

        if qr_data and qr_data != scanned_qr:
            print("QR Code Data:", qr_data)
            scanned_qr = qr_data

            qr_data_split = qr_data.split(", ")
            if len(qr_data_split) == 2 and qr_data_split[0].startswith("ID: ") and qr_data_split[1].startswith("Name: "):
                student_id = qr_data_split[0].replace("ID: ", "")
                student_name = qr_data_split[1].replace("Name: ", "")

                if student_id == matched_student_id:
                    try:
                        sql = "INSERT INTO attendance (student_id, date, in_time) VALUES (%s, CURDATE(), CURTIME())"
                        values = (student_id,)
                        cursor.execute(sql, values)
                        conn.commit()
                        print(f"✅ Attendance marked for {student_name} (ID: {student_id})")
                        break
                    except mysql.connector.Error as err:
                        print(f"[ERROR] Database error: {err}")

        if bbox is not None and qr_data:
            cv2.putText(frame, qr_data, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Main menu
def main_menu() -> None:
    while True:
        print("\n--- Attendance Management System ---")
        print("1. Register Student and Capture Image")
        print("2. Take Attendance")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            student_id = register_student()
            capture_image(student_id)
            generate_qr_codes_for_all_students()
        elif choice == '2':
            mark_attendance()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

# Run the system
main_menu()

# Close database
cursor.close()
conn.close()
