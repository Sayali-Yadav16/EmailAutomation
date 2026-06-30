import pandas as pd
import os
from datetime import datetime
import json

class RPAStatusTracker:
    """Helper class to track and update RPA automation status in Excel"""
    
    def __init__(self, excel_file="../patients.xlsx"):
        self.excel_file = excel_file
        self.log_file = "../automation.log"
        
    def add_status_column(self):
        """Add Status column to Excel if it doesn't exist"""
        try:
            df = pd.read_excel(self.excel_file)
            
            if "Status" not in df.columns:
                df["Status"] = "Pending"
                df["Processed_At"] = ""
                df.to_excel(self.excel_file, index=False)
                print("✓ Status column added to Excel")
                return True
            print("✓ Status column already exists")
            return False
        except Exception as e:
            print(f"❌ Error adding status column: {e}")
            return False
    
    def update_status(self, patient_name, status="Completed", timestamp=None):
        """Update patient status in Excel after processing"""
        try:
            df = pd.read_excel(self.excel_file)
            
            if timestamp is None:
                timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            # Find the row with matching patient name
            mask = df["Name"].str.strip().str.lower() == patient_name.strip().lower()
            
            if mask.any():
                df.loc[mask, "Status"] = status
                df.loc[mask, "Processed_At"] = timestamp
                df.to_excel(self.excel_file, index=False)
                
                print(f"✓ Updated {patient_name}: {status}")
                return True
            else:
                print(f"⚠ Patient '{patient_name}' not found in Excel")
                return False
                
        except Exception as e:
            print(f"❌ Error updating status: {e}")
            return False
    
    def get_summary(self):
        """Get automation summary from log file"""
        try:
            if not os.path.exists(self.log_file):
                return None
                
            with open(self.log_file, 'r') as f:
                content = f.read()
            
            summary = {
                "log_content": content,
                "success_count": content.count("[SUCCESS]"),
                "failed_count": content.count("[FAILED]"),
                "skipped_count": content.count("[SKIPPED]"),
            }
            return summary
        except Exception as e:
            print(f"❌ Error reading summary: {e}")
            return None
    
    def create_config(self):
        """Create automation config file"""
        config = {
            "automation_name": "Hospital Patient Registration & Appointment Booking",
            "version": "2.0",
            "features": [
                "Error handling with Try-Catch",
                "Dynamic file paths",
                "Status tracking in Excel",
                "Progress logging",
                "Timestamp in reports",
                "Input validation",
                "Summary reporting"
            ],
            "excel_file": "../patients.xlsx",
            "reports_folder": "../reports",
            "log_file": "../automation.log",
            "website_url": "http://localhost:3000",
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        
        with open("../automation_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✓ Config file created: automation_config.json")
        return config

# Usage Example (Can be called from UiPath via Python Activity)
if __name__ == "__main__":
    tracker = RPAStatusTracker()
    
    # Prepare Excel with status column
    tracker.add_status_column()
    
    # Create config file
    tracker.create_config()
    
    # Example: Update status (would be called by UiPath after each patient)
    # tracker.update_status("Sayali", "Completed")
    
    # Get summary
    summary = tracker.get_summary()
    if summary:
        print(f"\n📊 Summary: {summary['success_count']} successful, {summary['failed_count']} failed")
