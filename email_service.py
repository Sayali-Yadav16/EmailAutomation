import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ==================== EMAIL CONFIG ====================
# For Gmail: Use an "App Password" (NOT your regular password)
SMTP_SERVER   = "smtp.gmail.com"
SMTP_PORT     = 587
SENDER_EMAIL  = "sayali.yadav1619@gmail.com"  # Update with your email
SENDER_PASS   = "ydkegizgqefhzwem"          # Removed spaces (required for Gmail)
# ======================================================

def send_confirmation_email(patient_email, patient_name, pdf_path):
    """Sends a confirmation email with a PDF report attachment."""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return False

    try:
        # 1. Create message
        msg = MIMEMultipart()
        msg['From'] = f"CareSync Hospital <{SENDER_EMAIL}>"
        msg['To'] = patient_email
        msg['Subject'] = f"Appointment Confirmed: {patient_name}"

        body = f"""
        Dear {patient_name},

        Your appointment has been successfully confirmed by the CareSync Hospital RPA System.
        Please find your detailed medical report and appointment slot attached to this email.

        If you have any questions, please reply to this email or visit our portal.

        Best regards,
        The CareSync Hospital Team
        """
        msg.attach(MIMEText(body, 'plain'))

        # 2. Attach PDF
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(pdf_path)}'
            )
            msg.attach(part)

        # 3. Connect and send
        email_clean = SENDER_EMAIL.strip()
        pass_clean  = SENDER_PASS.strip()
        
        print(f"DEBUG: Attempting login for {email_clean}...")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(email_clean, pass_clean)
        server.send_message(msg)
        server.quit()
        
        print(f"✔ Email sent successfully to {patient_email}")
        return True

    except Exception as e:
        print(f"❌ Email Error: {e}")
        return False
