import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from functools import wraps
from email_service import send_confirmation_email

# ==================== MYSQL CONFIG ====================
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sayali@123',
    'database': 'hospital_rpa',
    'port': 3306
}

app = Flask(__name__)
app.secret_key = "super_secure_rpa_key_2026"

# ==================== DB CONNECTION ====================
def create_mysql_connection():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"DB Error: {e}")
    return None

# ==================== LOGIN DECORATOR ====================
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

# ==================== LOG FUNCTION ====================
def log_action(patient_id, action, status, msg=""):
    conn = create_mysql_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO automation_logs (patient_id, action, status, log_message) VALUES (%s,%s,%s,%s)",
            (patient_id, action, status, msg)
        )
        conn.commit()
    except Error as e:
        print(f"Log Error: {e}")
    finally:
        cursor.close()
        conn.close()

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')


# ==================== DB INITIALIZATION ====================
def init_db():
    conn = create_mysql_connection()
    if not conn:
        print("Could not initialize database - connection failed")
        return
    try:
        cursor = conn.cursor()
        # Create patients table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                age INT NOT NULL,
                email VARCHAR(255) NOT NULL,
                doctor VARCHAR(100),
                appointment_date DATE,
                slot VARCHAR(50),
                priority VARCHAR(50) DEFAULT 'Normal',
                status VARCHAR(50) DEFAULT 'Pending',
                rpa_processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Ensure 'rpa_processed' column exists (in case table was created with old schema)
        cursor.execute("SHOW COLUMNS FROM patients LIKE 'rpa_processed'")
        if not cursor.fetchone():
            print("Adding missing column 'rpa_processed' to patients table...")
            cursor.execute("ALTER TABLE patients ADD COLUMN rpa_processed BOOLEAN DEFAULT FALSE AFTER status")

        # Ensure other potentially missing columns exist
        cursor.execute("SHOW COLUMNS FROM patients LIKE 'doctor'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE patients ADD COLUMN doctor VARCHAR(100) AFTER email")
            
        cursor.execute("SHOW COLUMNS FROM patients LIKE 'appointment_date'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE patients ADD COLUMN appointment_date DATE AFTER doctor")

        cursor.execute("SHOW COLUMNS FROM patients LIKE 'slot'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE patients ADD COLUMN slot VARCHAR(50) AFTER appointment_date")

        cursor.execute("SHOW COLUMNS FROM patients LIKE 'priority'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE patients ADD COLUMN priority VARCHAR(50) DEFAULT 'Normal' AFTER slot")

        cursor.execute("SHOW COLUMNS FROM patients LIKE 'status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE patients ADD COLUMN status VARCHAR(50) DEFAULT 'Pending' AFTER priority")

        # Create automation_logs table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automation_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                action VARCHAR(255),
                status VARCHAR(50),
                log_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("Database verification/initialization complete")
    except Error as e:
        print(f"Init Error: {e}")
    finally:
        cursor.close()
        conn.close()

# ==================== PDF REPORT GENERATOR ====================
# ==================== PDF REPORT GENERATOR ====================
try:
    from fpdf import FPDF
except ImportError:
    # Fallback to fpdf2 if installed, or just handle missing gracefully
    try:
        from fpdf import FPDF
    except ImportError:
        print("Warning: fpdf not found. Report generation will fail.")
        FPDF = object # Dummy for class inheritance


class PatientPDF(FPDF):
    def header(self):
        self.set_fill_color(11, 17, 32)
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('Arial', 'B', 15)
        self.set_text_color(56, 189, 248)
        self.cell(0, 10, 'CareSync Hospital - Medical Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()} | Generated by CareSync RPA', 0, 0, 'C')

def generate_patient_pdf(patient_data):
    """Generates a PDF report for a single patient and returns the file path."""
    try:
        p = patient_data
        pdf = PatientPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Patient Info Section
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(56, 189, 248)
        pdf.cell(0, 10, "PATIENT INFORMATION", 1, 1, 'L', True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(50, 10, "Name:", 0)
        pdf.cell(0, 10, str(p['name']), 0, 1)
        pdf.cell(50, 10, "Age:", 0)
        pdf.cell(0, 10, str(p['age']), 0, 1)
        pdf.cell(50, 10, "Email:", 0)
        pdf.cell(0, 10, str(p['email']), 0, 1)
        
        pdf.ln(5)
        
        # Appointment Section
        pdf.set_text_color(56, 189, 248)
        pdf.cell(0, 10, "APPOINTMENT DETAILS", 1, 1, 'L', True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(50, 10, "Doctor:", 0)
        pdf.cell(0, 10, str(p['doctor']), 0, 1)
        pdf.cell(50, 10, "Date:", 0)
        pdf.cell(0, 10, str(p['appointment_date']), 0, 1)
        pdf.cell(50, 10, "Slot:", 0)
        pdf.cell(0, 10, str(p['slot']), 0, 1)
        pdf.cell(50, 10, "Priority:", 0)
        pdf.cell(0, 10, str(p['priority']), 0, 1)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 10)
        pdf.multi_cell(0, 10, "Disclaimer: This is an automatically generated report by the CareSync RPA system. For official medical use, please consult with your assigned doctor.")

        # Save to reports folder
        report_name = f"Report_{p['name'].replace(' ', '_')}.pdf"
        output_path = os.path.join('reports', report_name)
        pdf.output(output_path)
        return output_path

    except Exception as e:
        print(f"PDF Gen Error: {e}")
        return None

@app.route('/download_report/<int:id>')
@login_required
def download_report(id):
    conn = create_mysql_connection()
    if not conn:
        return "Database Connection Failed", 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE id = %s", (id,))
        p = cursor.fetchone()
        
        if not p:
            return "Patient Not Found", 404

        output_path = generate_patient_pdf(p)
        if not output_path:
            return "Report generation failed", 500
            
        from flask import send_file
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"PDF Error: {e}")
        return str(e), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        conn.close()

# ---------------- FULL EXCEL REPORT ----------------
@app.route('/download_all_data')
@login_required
def download_all_data():
    import pandas as pd
    from io import BytesIO
    from flask import send_file

    conn = create_mysql_connection()
    if not conn:
        return "Database Connection Failed", 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, age, email, doctor, appointment_date, slot, priority, status, rpa_processed, created_at FROM patients ORDER BY created_at DESC")
        data = cursor.fetchall()
        
        if not data:
            flash("No patient data to export")
            return redirect('/dashboard')

        df = pd.DataFrame(data)
        
        # Format dates for Excel
        if 'appointment_date' in df.columns:
            df['appointment_date'] = df['appointment_date'].astype(str)
        if 'created_at' in df.columns:
            df['created_at'] = df['created_at'].astype(str)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='All Patients')
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name="CareSync_Patients_Full_Report.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        print(f"Excel Export Error: {e}")
        return f"Export failed: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()


# ---------------- INDIVIDUAL ACTIONS ----------------
@app.route('/confirm_appointment/<int:id>')
@login_required
def confirm_appointment(id):
    conn = create_mysql_connection()
    if not conn: return "DB Error", 500
    try:
        cursor = conn.cursor(dictionary=True)
        # Update first
        cursor.execute("UPDATE patients SET status = 'Confirmed' WHERE id = %s", (id,))
        
        # Fetch updated info for email
        cursor.execute("SELECT * FROM patients WHERE id = %s", (id,))
        p = cursor.fetchone()
        
        conn.commit()
        log_action(id, "APPOINTMENT_CONFIRM", "SUCCESS", "Appointment confirmed through dashboard")
        
        # 1. Generate PDF Report
        report_path = generate_patient_pdf(p)
        
        # 2. Send Automated Email
        if report_path:
            email_status = send_confirmation_email(p['email'], p['name'], report_path)
            if email_status:
                flash(f"Patient #{id} confirmed & emailed successfully")
            else:
                flash(f"Patient #{id} confirmed, but email notification failed")
        else:
            flash(f"Patient #{id} confirmed, but report generation failed")

    except Exception as e: 
        print(f"Confirm Error: {e}")
        flash(f"Error: {str(e)}")
    finally: conn.close()
    return redirect('/dashboard')

@app.route('/mark_processed/<int:id>')
@login_required
def mark_processed(id):
    conn = create_mysql_connection()
    if not conn: return "DB Error", 500
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE patients SET rpa_processed = TRUE WHERE id = %s", (id,))
        conn.commit()
        log_action(id, "RPA_MARK", "SUCCESS", "Patient marked as RPA Processed")
        flash(f"Patient #{id} marked as processed")
    except Exception as e: flash(str(e))
    finally: conn.close()
    return redirect('/dashboard')


# ---------------- REGISTER ----------------
@app.route('/register', methods=['POST'])
def register():
    conn = None
    try:
        name = request.form.get('name')
        age_str = request.form.get('age', '0')
        age = int(age_str) if age_str.isdigit() else 0
        email = request.form.get('email')
        doctor = request.form.get('doctor', 'General')
        date = request.form.get('date')
        slot = request.form.get('slot', '10:00 AM')

        print(f"DEBUG: Registering patient {name}, Date: {date}")

        if not name or not email:
            flash("Name and Email are required")
            return redirect('/')

        # Handle empty date (MySQL DATE doesn't like empty string)
        sql_date = date if (date and date.strip()) else None

        # Simple Priority Logic
        priority = "High Priority" if (age > 60 or doctor == 'Cardiologist') else "Normal"

        conn = create_mysql_connection()
        if not conn:
            flash("Database connection failed")
            return redirect('/')

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO patients (name, age, email, doctor, appointment_date, slot, priority, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, age, email, doctor, sql_date, slot, priority, 'Pending'))

        pid = cursor.lastrowid
        conn.commit()

        # Get total for display on success page
        cursor.execute("SELECT COUNT(*) as c FROM patients")
        total = cursor.fetchone()[0]

        log_action(pid, "REGISTER", "SUCCESS", f"{name} registered via form")

        patient_data = {
            "name": name, "age": age, "email": email,
            "doctor": doctor, "date": date, "slot": slot
        }

        return render_template('success.html', patient=patient_data, total=total)

    except Exception as e:
        print(f"Register Error: {e}")
        flash(f"Error: {str(e)}")
        return redirect('/')
    finally:
        if conn:
            conn.close()

# ---------------- SIMULATE RPA ----------------
@app.route('/run_rpa_simulation')
@login_required
def run_rpa_simulation():
    conn = create_mysql_connection()
    if not conn:
        return jsonify({"error": "DB failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Fetch pending patients
        cursor.execute("SELECT id, name FROM patients WHERE status = 'Pending'")
        pending = cursor.fetchall()
        
        if not pending:
            flash("No pending patients to process")
            return redirect('/dashboard')

        for p in pending:
            # Update status to 'Confirmed' and 'rpa_processed' to TRUE
            cursor.execute("""
                UPDATE patients 
                SET status = 'Confirmed', rpa_processed = TRUE 
                WHERE id = %s
            """, (p['id'],))
            
            # Log the RPA action
            log_action(p['id'], "RPA_PROCESS", "SUCCESS", f"RPA bot automatically confirmed appointment for {p['name']}")
        
        conn.commit()
        flash(f"Successfully processed {len(pending)} patients via RPA Simulation")
        return redirect('/dashboard')

    except Exception as e:
        print(f"RPA Error: {e}")
        flash(f"RPA Simulation failed: {str(e)}")
        return redirect('/dashboard')
    finally:
        cursor.close()
        conn.close()


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
            session['logged_in'] = True
            session['username'] = 'Admin'
            return redirect('/dashboard')
        flash("Invalid login")
    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
@login_required
def dashboard():
    conn = create_mysql_connection()
    if not conn:
        flash("Database connection failed")
        return redirect('/login')

    try:
        cursor = conn.cursor(dictionary=True)

        # Get Unique Patients (latest per email)
        cursor.execute("""
            SELECT * FROM patients 
            WHERE id IN (SELECT MAX(id) FROM patients GROUP BY email)
            ORDER BY created_at DESC
        """)
        patients = cursor.fetchall()

        # Stats calculations
        cursor.execute("SELECT COUNT(*) as c FROM patients")
        total_res = cursor.fetchone()
        total = total_res['c'] if total_res else 0

        cursor.execute("SELECT COUNT(*) as c FROM patients WHERE priority='High Priority'")
        high_res = cursor.fetchone()
        high = high_res['c'] if high_res else 0

        cursor.execute("SELECT COUNT(*) as c FROM patients WHERE status='Confirmed'")
        conf_res = cursor.fetchone()
        confirmed = conf_res['c'] if conf_res else 0

        cursor.execute("SELECT COUNT(*) as c FROM patients WHERE status='Pending'")
        pend_res = cursor.fetchone()
        pending = pend_res['c'] if pend_res else 0

        cursor.execute("SELECT COUNT(*) as c FROM patients WHERE rpa_processed=TRUE")
        proc_res = cursor.fetchone()
        processed = proc_res['c'] if proc_res else 0

        # Today's appointments
        cursor.execute("SELECT COUNT(*) as c FROM patients WHERE appointment_date = CURDATE()")
        today_res = cursor.fetchone()
        today_count = today_res['c'] if today_res else 0

        # Processing rate
        rate = round((processed / total * 100), 1) if total > 0 else 0

        # Doctor stats
        cursor.execute("SELECT doctor, COUNT(*) as count FROM patients GROUP BY doctor")
        doc_stats = cursor.fetchall()

        stats = {
            "total": total,
            "confirmed": confirmed,
            "pending": pending,
            "high_priority": high,
            "processed": processed,
            "processing_rate": rate,
            "today": today_count
        }

        return render_template('dashboard_mysql.html', patients=patients, stats=stats, doctor_stats=doc_stats)

    except Error as e:
        print(f"Dashboard Query Error: {e}")
        flash(f"Database error: {str(e)}")
        return redirect('/login')

    finally:
        if 'cursor' in locals(): cursor.close()
        conn.close()

# ---------------- LOGS ----------------
@app.route('/admin/logs')
@login_required
def admin_logs():
    conn = create_mysql_connection()
    if not conn: return "DB Error", 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.*, p.name as patient_name 
            FROM automation_logs l 
            LEFT JOIN patients p ON l.patient_id = p.id 
            ORDER BY l.created_at DESC 
            LIMIT 100
        """)
        logs = cursor.fetchall()
        return render_template('admin_logs.html', logs=logs)
    except Error as e: flash(str(e))
    finally: conn.close()
    return redirect('/dashboard')

@app.route('/clear_logs')
@login_required
def clear_logs():
    conn = create_mysql_connection()
    if not conn: return "DB Error", 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM automation_logs")
        conn.commit()
        flash("Logs cleared successfully")
    except Error as e: flash(str(e))
    finally: conn.close()
    return redirect('/admin/logs')

# ---------------- SETTINGS ----------------
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        # Simulate saving settings
        flash("System settings updated successfully")
        return redirect('/admin/settings')
    return render_template('admin_settings.html')

# ---------------- API ----------------
@app.route('/api/patients')
def api_patients():
    conn = create_mysql_connection()
    if not conn:
        return jsonify({"error": "DB failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients")
        data = cursor.fetchall()
        return jsonify(data)

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ==================== MAIN ====================
if __name__ == '__main__':
    os.makedirs('reports', exist_ok=True)
    init_db()  # Initialize database and tables
    print("Server running at http://localhost:3000")
    app.run(debug=True, port=3000)
