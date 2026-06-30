import mysql.connector
import pandas as pd
import os
from datetime import datetime

# ==================== CONFIG ====================
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sayali@123',
    'database': 'hospital_rpa',
}
OUTPUT_FILE = r"d:\SEM 6\RPA\RPA Project\reports\Master_Patient_Report.xlsx"
# ================================================

def generate_master_report():
    print("🚀 Generating Master Automation Report...")
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        # Fetch all patient details
        query = """
            SELECT 
                id as 'Patient ID', 
                name as 'Name', 
                age as 'Age', 
                email as 'Email', 
                doctor as 'Doctor', 
                appointment_date as 'Appt Date', 
                slot as 'Slot', 
                priority as 'Priority', 
                status as 'Automation Status',
                created_at as 'Registered On'
            FROM patients
            ORDER BY created_at DESC
        """
        df = pd.read_sql(query, conn)
        
        # Ensure reports directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Save to Excel
        with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Automation Results')
            
            # Formatting (Optional but looks premium)
            workbook  = writer.book
            worksheet = writer.sheets['Automation Results']
            header_format = workbook.add_format({'bold': True, 'bg_color': '#38bdf8', 'font_color': 'white'})
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20)

        print(f"✅ Successful! Master report saved to: {OUTPUT_FILE}")
        
        # HOUSEKEEPING: Delete the old separate .txt reports to clean up
        reports_dir = os.path.dirname(OUTPUT_FILE)
        for f in os.listdir(reports_dir):
            if f.endswith("_report.txt"):
                os.remove(os.path.join(reports_dir, f))
        print("🧹 Cleaned up separate .txt report files.")

    except Exception as e:
        print(f"❌ Error generating master report: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    generate_master_report()
