# 🏥 Hospital RPA Automation System

> An intelligent Robotic Process Automation (RPA) solution that automates hospital patient registration, appointment management, report generation, and workflow tracking using **UiPath**, **Python Flask**, and **MySQL**.

---

## 📌 Project Overview

The Hospital RPA Automation System streamlines hospital administrative operations by automating patient registration, appointment booking, status tracking, and medical report generation. The solution combines **UiPath RPA workflows** with a **Python Flask backend** to minimize manual effort, improve operational efficiency, and maintain centralized patient records.

---

## ✨ Key Features

- 🤖 Automated patient registration using UiPath
- 📅 Appointment booking and management
- 👨‍⚕️ Patient record management with MySQL
- 📊 Real-time web dashboard
- 📄 Automated PDF medical report generation
- 📈 Excel-based patient data processing
- 🔄 RPA status tracking and audit logging
- 🔐 Secure administrator login

---

## 🏗️ System Architecture

```
                 User
                  │
                  ▼
         Flask Web Dashboard
                  │
                  ▼
            MySQL Database
                  ▲
                  │
        UiPath RPA Workflow
                  │
       Patient Excel Dataset
                  │
                  ▼
     PDF Report Generation & Logs
```

---

## ⚙️ Project Structure

```
Hospital-RPA-Automation/
│
├── server.py                 # Flask backend and dashboard
├── report_builder.py         # Generates patient PDF reports
├── status_tracker.py         # Updates RPA processing status
├── setup_test_data.py        # Creates sample patient records
├── patients.xlsx             # Input patient dataset
│
├── HospitalAutomation/
│   └── Main.xaml             # UiPath automation workflow
│
├── templates/                # HTML templates
│   ├── dashboard.html
│   ├── login.html
│   └── registration.html
│
├── reports/                  # Generated reports
│
└── README.md
```

---

## 🛠 Tech Stack

| Layer | Technology |
|--------|------------|
| RPA | UiPath |
| Backend | Python Flask |
| Database | MySQL |
| Frontend | HTML, CSS, JavaScript |
| Reporting | ReportLab |
| Data Source | Excel |
| Automation | UiPath Studio |

---

## 🚀 Getting Started

### 1. Generate Sample Data

```bash
python setup_test_data.py
```

### 2. Start the Flask Server

```bash
python server.py
```

Open your browser:

```
http://localhost:3000/dashboard
```

**Default Credentials**

```
Username: admin
Password: admin123
```

### 3. Run the UiPath Automation

- Open **HospitalAutomation/Main.xaml** in UiPath Studio.
- Click **Run** to execute the automation workflow.

---

## 🗄 Database

The application automatically creates the required database schema during startup.

### Database

- **hospital_rpa**

### Tables

- **patients** – Stores patient details and appointment information.
- **automation_logs** – Maintains logs of all automation activities.

---

## 🔄 Workflow

1. Generate or import patient data from Excel.
2. Launch the Flask application.
3. Run the UiPath automation.
4. Patient records are processed automatically.
5. Status is updated in MySQL.
6. PDF reports are generated.
7. Dashboard displays processed records and automation status.

---

## 📊 Core Modules

- Patient Registration
- Appointment Management
- UiPath Automation Workflow
- Status Tracking
- Medical Report Generation
- Dashboard & Analytics
- Audit Logging

---

## 🔮 Future Enhancements

- Email and SMS appointment notifications
- OCR integration for patient forms
- Cloud database support
- Role-based authentication
- AI-assisted patient scheduling
- Hospital Management System integration

---

## 👩‍💻 Author

**Sayali Yadav**

Computer Engineering Student

Interested in Robotic Process Automation (RPA), Full-Stack Development, Artificial Intelligence, and Software Engineering.
