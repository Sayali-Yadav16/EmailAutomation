# 🏥 Hospital RPA Automation Project

## 🎯 Overview
Automated hospital patient registration and appointment booking system using UiPath RPA and a Python Flask backend.

## 📂 Project Structure (Cleaned & Manageable)
- **server.py**: Core Flask backend with MySQL integration and dashboard.
- **report_builder.py**: Generates themed PDF medical reports for patients.
- **status_tracker.py**: Helper to update Excel status from the RPA bot.
- **setup_test_data.py**: Script to generate sample patient data in Excel.
- **HospitalAutomation/**: Contains the UiPath `Main.xaml` workflow.
- **patients.xlsx**: Main data source for the automation.
- **templates/**: HTML views (Dashboard, Login, Registration).
- **reports/**: Folder where generated PDF/Text reports are saved.

## 🚀 Quick Start
1. **Initialize Data**:
   ```powershell
   python setup_test_data.py
   ```
2. **Start Backend**:
   ```powershell
   python server.py
   ```
   *Dashboard available at: http://localhost:3000/dashboard*
   *Login: `admin` / `admin123`*

3. **Run Automation**:
   - Open `HospitalAutomation/Main.xaml` in UiPath.
   - Click **Run**.

## 🔧 Database Details
The system automatically creates and verifies its database on startup.
- **Database**: `hospital_rpa` (MySQL)
- **Primary Table**: `patients` (Stores names, ages, doctors, and RPA status)
- **Audit Table**: `automation_logs` (Tracks every bot action)

## 🛑 Common Fixes
- **Login Issues**: Ensure `server.py` is running and the database connection is healthy.
- **Column Errors**: The system now automatically adds missing columns like `rpa_processed`.
- **Reports Folder**: If reports are not saved, ensure the `/reports` folder exists (the server creates it automatically).

---
**Last Updated:** 28-03-2026 | **Status:** Manageable & Production Ready ✅
