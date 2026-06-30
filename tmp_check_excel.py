import pandas as pd
import os

excel_path = r"d:\SEM 6\RPA\RPA Project\HospitalAutomation\reports\Processed_Patients.xlsx"
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    print(f"Total Rows: {len(df)}")
    print(df.head())
else:
    print("File not found.")
