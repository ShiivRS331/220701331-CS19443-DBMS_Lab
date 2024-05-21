import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QTextEdit, QRadioButton
from PyQt5.QtGui import QPixmap
import mysql.connector
import random
import string

# Establish MySQL connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="shiivrs@9/11/2004",
    database="dbms"
)    # Replace "your_password" with your MySQL password and update the database name if necessary
cursor = db_connection.cursor()

# Global variables to store windows
login_window = None
doctor_window = None
patient_window = None

def show_login_window():
    global login_window
    if login_window is None:
        login_window = LoginWindow()
        login_window.show()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(500, 200, 500, 500)

        layout = QVBoxLayout()

        # Background image setup
        background_label = QLabel(self)
        pixmap = QPixmap("bg-image.jpeg")  # Provide the path to your background image
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, 500, 500)  # Set geometry to cover the window
        background_label.setScaledContents(True)  # Scale the image to fit the label
        heading_label = QLabel("DR DOCS", self)
        heading_label.setStyleSheet("font-size: 24px;color:white;")  # Set font size
        heading_label.setAlignment(Qt.AlignCenter)  # Center align the heading
        layout.addWidget(heading_label)
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color:white;")  # Set font size
        self.username_input = QLineEdit()
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        password_label = QLabel("Password:")
        password_label.setStyleSheet("color:white;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        role_label = QLabel("Role:")
        role_label.setStyleSheet("color:white;")
        layout.addWidget(role_label)

        self.doctor_radio = QRadioButton("Doctor")
        self.doctor_radio.setStyleSheet("color:white;")
        self.patient_radio = QRadioButton("Patient")
        self.patient_radio.setStyleSheet("color:white;")
        layout.addWidget(self.doctor_radio)
        layout.addWidget(self.patient_radio)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = "Doctor" if self.doctor_radio.isChecked() else "Patient"
        global cursor
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND role = %s", (username, password, role.lower()))
        user = cursor.fetchone()
    
        if user:
            if role.lower() == 'doctor':
                open_doctor_window()
            elif role.lower() == 'patient':
                cursor.execute("SELECT first_login FROM patients WHERE username = %s", (username,))
                first_login = cursor.fetchone()[0]
                if first_login:
                    open_change_credentials_window(username)
                else:
                    open_patient_window(username)
        else:
            QMessageBox.warning(None, "Login Failed", "Invalid username, password, or role.")

class ChangeCredentialsWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Change Username and Password")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        new_username_label = QLabel("New Username:")
        self.new_username_input = QLineEdit()
        layout.addWidget(new_username_label)
        layout.addWidget(self.new_username_input)

        new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(new_password_label)
        layout.addWidget(self.new_password_input)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_credentials)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_credentials(self):
        new_username = self.new_username_input.text()
        new_password = self.new_password_input.text()
        
        global cursor, db_connection
        cursor.execute("UPDATE users SET username = %s, password = %s WHERE username = %s", (new_username, new_password, self.username))
        cursor.execute("UPDATE patients SET username = %s, password = %s, first_login = %s WHERE username = %s", (new_username, new_password, False, self.username))
        db_connection.commit()

        QMessageBox.information(self, "Success", "Credentials updated successfully.")
        self.close()
        open_patient_window(new_username)

def open_change_credentials_window(username):
    global change_credentials_window
    change_credentials_window = ChangeCredentialsWindow(username)
    change_credentials_window.show()


def open_doctor_window():
    global login_window, doctor_window
    login_window.close()  # Close the login window if open
    doctor_window = DoctorWindow()
    doctor_window.show()

class DoctorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doctor Options")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        new_entry_button = QPushButton("Make New Patient Entry")
        new_entry_button.clicked.connect(make_new_entry)
        layout.addWidget(new_entry_button)

        update_entry_button = QPushButton("Update Old Patient Entry")
        update_entry_button.clicked.connect(update_entry)
        layout.addWidget(update_entry_button)

        self.setLayout(layout)

def open_patient_window(username):
    global login_window, patient_window
    login_window.close()  # Close the login window if open
    patient_window = PatientWindow(username)
    patient_window.show()

class PatientWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Patient Report")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Fetch patient report from the database based on username
        global cursor
        cursor.execute("SELECT * FROM patients WHERE username = %s", (username,))
        patient_data = cursor.fetchone()
        report_label = QLabel("PATIENT REPORT")
        layout.addWidget(report_label)

        if patient_data:
            heading_label = QLabel("Patient Report")     
            heading_label.setStyleSheet('font-size:24px;')       
            report_label = QLabel()
            report_label.setText(f"Name: {patient_data[1]}\n"
                                 f"Age: {patient_data[2]}\n"
                                 f"Family History of Diseases: {patient_data[3]}\n"
                                 f"Previous Surgeries: {patient_data[4]}\n"
                                 f"Allergies: {patient_data[5]}\n"
                                 f"Symptoms: {patient_data[6]}\n"
                                 f"Diagnosis: {patient_data[7]}\n"
                                 f"Tests: {patient_data[8]}\n"
                                 f"Medications: {patient_data[9]}\n"
                                 f"Report: {patient_data[10]}")
            layout.addWidget(report_label)
        else:
            QMessageBox.warning(None, "Error", "Patient data not found.")

        self.setLayout(layout)
new_entry_window = None
update_window = None

def make_new_entry():
    global new_entry_window
    new_entry_window = QWidget()
    new_entry_window.setWindowTitle("New Patient Entry")
    new_entry_window.setGeometry(100, 100, 400, 400)

    layout = QVBoxLayout()
    # Labels and text edits for patient details
    #name
    name_label = QLabel("Name:")
    name_edit = QLineEdit()
    layout.addWidget(name_label)
    layout.addWidget(name_edit)
    #age
    age_label = QLabel("Age:")
    age_edit = QLineEdit()
    layout.addWidget(age_label)
    layout.addWidget(age_edit)
    # Family history of diseases
    family_history_label = QLabel("Family History of Diseases:")
    family_history_edit = QTextEdit()
    layout.addWidget(family_history_label)
    layout.addWidget(family_history_edit)
    # Previous surgeries
    surgeries_label = QLabel("Previous Surgeries:")
    surgeries_edit = QTextEdit()
    layout.addWidget(surgeries_label)
    layout.addWidget(surgeries_edit)
    # Allergies
    allergies_label = QLabel("Allergies:")
    allergies_edit = QTextEdit()
    layout.addWidget(allergies_label)
    layout.addWidget(allergies_edit)
    # Symptoms
    symptoms_label = QLabel("Symptoms:")
    symptoms_edit = QTextEdit()
    layout.addWidget(symptoms_label)
    layout.addWidget(symptoms_edit)
    # Diagnosis
    diagnosis_label = QLabel("Diagnosis:")
    diagnosis_edit = QTextEdit()
    layout.addWidget(diagnosis_label)
    layout.addWidget(diagnosis_edit)
    # Tests
    tests_label = QLabel("Tests:")
    tests_edit = QTextEdit()
    layout.addWidget(tests_label)
    layout.addWidget(tests_edit)
    # Medications
    medications_label = QLabel("Medications:")
    medications_edit = QTextEdit()
    layout.addWidget(medications_label)
    layout.addWidget(medications_edit)

    save_button = QPushButton("Save")
    save_button.clicked.connect(lambda: save_patient_entry(name_edit.text(), age_edit.text(), family_history_edit.toPlainText(), surgeries_edit.toPlainText(), allergies_edit.toPlainText(), symptoms_edit.toPlainText(), diagnosis_edit.toPlainText(), tests_edit.toPlainText(), medications_edit.toPlainText()))
    layout.addWidget(save_button)

    new_entry_window.setLayout(layout)
    new_entry_window.show()

def save_patient_entry(name, age, family_history, surgeries, allergies, symptoms, diagnosis, tests, medications):
    # Use global cursor object
    global cursor
    # Generate random username and password for the patient
    patient_username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    patient_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Insert patient details, username, and password into the database
    insert_query_patient = "INSERT INTO patients (name, age, family_history, surgeries, allergies, symptoms, diagnosis, tests, medications, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query_patient, (name, age, family_history, surgeries, allergies, symptoms, diagnosis, tests, medications, patient_username, patient_password))
    
    # Insert patient details into the users table
    insert_query_user = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
    cursor.execute(insert_query_user, (patient_username, patient_password, 'patient'))
    
    db_connection.commit()
    QMessageBox.information(None, "Success", "Patient entry saved successfully. Username: {}, Password: {}".format(patient_username, patient_password))

def update_entry():
    global update_window
    update_window = QWidget()
    update_window.setWindowTitle("Update Patient Entry")
    update_window.setGeometry(100, 100, 400, 150)

    layout = QVBoxLayout()

    patient_name_label = QLabel("Patient Name:")
    patient_name_edit = QLineEdit()
    layout.addWidget(patient_name_label)
    layout.addWidget(patient_name_edit)

    fetch_button = QPushButton("Fetch Details")
    fetch_button.clicked.connect(lambda: fetch_patient_details_by_name(patient_name_edit.text()))
    layout.addWidget(fetch_button)

    update_window.setLayout(layout)
    update_window.show()

def fetch_patient_details_by_name(patient_name):
    global cursor, update_patient_window
    cursor.execute("SELECT * FROM patients WHERE name = %s", (patient_name,))
    patient_data = cursor.fetchone()

    if patient_data:
        # Ensure update_patient_window is a global variable
        update_patient_window = QWidget()
        update_patient_window.setWindowTitle("Update Patient Details")
        update_patient_window.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        # Name
        name_label = QLabel("Name:")
        name_edit = QLineEdit(patient_data[1])
        layout.addWidget(name_label)
        layout.addWidget(name_edit)

        # Age
        age_label = QLabel("Age:")
        age_edit = QLineEdit(str(patient_data[2]))
        layout.addWidget(age_label)
        layout.addWidget(age_edit)

        # Family history of diseases
        family_history_label = QLabel("Family History of Diseases:")
        family_history_edit = QTextEdit(patient_data[3])
        layout.addWidget(family_history_label)
        layout.addWidget(family_history_edit)

        # Previous surgeries
        surgeries_label = QLabel("Previous Surgeries:")
        surgeries_edit = QTextEdit(patient_data[4])
        layout.addWidget(surgeries_label)
        layout.addWidget(surgeries_edit)

        # Allergies
        allergies_label = QLabel("Allergies:")
        allergies_edit = QTextEdit(patient_data[5])
        layout.addWidget(allergies_label)
        layout.addWidget(allergies_edit)

        # Symptoms
        symptoms_label = QLabel("Symptoms:")
        symptoms_edit = QTextEdit(patient_data[6])
        layout.addWidget(symptoms_label)
        layout.addWidget(symptoms_edit)

        # Diagnosis
        diagnosis_label = QLabel("Diagnosis:")
        diagnosis_edit = QTextEdit(patient_data[7])
        layout.addWidget(diagnosis_label)
        layout.addWidget(diagnosis_edit)

        # Tests
        tests_label = QLabel("Tests:")
        tests_edit = QTextEdit(patient_data[8])
        layout.addWidget(tests_label)
        layout.addWidget(tests_edit)

        # Medications
        medications_label = QLabel("Medications:")
        medications_edit = QTextEdit(patient_data[9])
        layout.addWidget(medications_label)
        layout.addWidget(medications_edit)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: save_updated_patient_details(patient_data[0], name_edit.text(), age_edit.text(), family_history_edit.toPlainText(), surgeries_edit.toPlainText(), allergies_edit.toPlainText(), symptoms_edit.toPlainText(), diagnosis_edit.toPlainText(), tests_edit.toPlainText(), medications_edit.toPlainText()))
        layout.addWidget(save_button)

        update_patient_window.setLayout(layout)
        update_patient_window.show()
    else:
        QMessageBox.warning(None, "Error", "Patient with name '{}' not found.".format(patient_name))

def save_updated_patient_details(patient_id, name, age, family_history, surgeries, allergies, symptoms, diagnosis, tests, medications):
    global cursor, db_connection
    update_query = "UPDATE patients SET name = %s, age = %s, family_history = %s, surgeries = %s, allergies = %s, symptoms = %s, diagnosis = %s, tests = %s, medications = %s WHERE id = %s"
    cursor.execute(update_query, (name, age, family_history, surgeries, allergies, symptoms, diagnosis, tests, medications, patient_id))
    db_connection.commit()

    QMessageBox.information(None, "Success", "Patient details updated successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    show_login_window()
    sys.exit(app.exec_())
