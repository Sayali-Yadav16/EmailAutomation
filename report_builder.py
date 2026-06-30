"""
CareSync Hospital - PDF Report Generator
Reads patients.xlsx and creates a themed PDF report for every patient.
Run: python generate_reports.py
"""
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
try:
    from fpdf.enums import Align
except ImportError:
    # Older versions of fpdf2 or original fpdf might have it differently
    try:
        from fpdf import Align
    except ImportError:
        # Fallback if Align is not findable
        class Align:
            L = "L"
            C = "C"
            R = "R"


REPORTS_DIR = "reports"
EXCEL_FILE  = "patients.xlsx"

# ── Colour palette matching the dark dashboard ───────────────────────────────
BG_DARK  = (11,  17,  32)   # #0b1120 – outer dark background
SURFACE  = (30,  41,  59)   # #1e293b – card surface
PRIMARY  = (56, 189, 248)   # #38bdf8 – sky-blue accent
SUCCESS  = (16, 185, 129)   # #10b981 – green
DANGER   = (239, 68,  68)   # #ef4444 – red / high-priority
MUTED    = (148, 163, 184)  # #94a3b8 – secondary text
WHITE    = (248, 250, 252)  # #f8fafc – main text
# ─────────────────────────────────────────────────────────────────────────────


class CareReport(FPDF):
    def __init__(self, patient_id):
        super().__init__()
        self.patient_id = patient_id

    # ──────────────────────── HEADER ────────────────────────────────────────
    def header(self):
        # Full-width dark bar
        self.set_fill_color(*BG_DARK)
        self.rect(0, 0, 210, 28, "F")

        # Hospital name (left)
        self.set_xy(12, 8)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*PRIMARY)
        self.cell(100, 10, "CareSync Hospital", align="L")

        # Badge – right
        self.set_xy(130, 9)
        self.set_fill_color(*SURFACE)
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.4)
        self.rect(130, 9, 68, 10, "FD")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.set_xy(130, 11)
        self.cell(68, 7, f"RPA Automation Report  |  {self.patient_id}", align="C")

        # Thin accent line under header
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.8)
        self.line(0, 28, 210, 28)
        self.ln(10)

    # ──────────────────────── FOOTER ────────────────────────────────────────
    def footer(self):
        self.set_y(-16)
        self.set_fill_color(*BG_DARK)
        self.rect(0, self.get_y(), 210, 20, "F")

        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.set_x(12)
        self.cell(90, 8,
                  f"Generated: {datetime.now().strftime('%d %b %Y  %H:%M')}  •  CareSync RPA Bot",
                  align="L")
        self.set_x(110)
        self.cell(88, 8, f"Page {self.page_no()}", align="R")

    # ──────────────────────── HELPERS ───────────────────────────────────────
    def section_title(self, title: str):
        """Dark section header bar."""
        self.set_fill_color(*SURFACE)
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.3)
        self.rect(12, self.get_y(), 186, 9, "FD")

        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*PRIMARY)
        self.set_xy(14, self.get_y() + 1)
        self.cell(182, 7, title.upper(), align="L")
        self.ln(11)

    def kv_row(self, label: str, value: str, highlight=False):
        """Key-value row inside a card."""
        y = self.get_y()
        # alternating background
        if highlight:
            self.set_fill_color(30, 45, 70)
        else:
            self.set_fill_color(20, 30, 50)
        self.rect(12, y, 186, 9, "F")

        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MUTED)
        self.set_xy(16, y + 1)
        self.cell(55, 7, label.upper(), align="L")

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*WHITE)
        self.set_xy(72, y + 1)
        self.cell(122, 7, str(value), align="L")
        self.ln(10)

    def priority_badge(self, priority: str):
        """Coloured priority badge block."""
        y   = self.get_y()
        is_hp = priority == "High Priority"
        fill  = DANGER if is_hp else SUCCESS

        self.set_fill_color(*fill)
        self.set_draw_color(*fill)
        badge_w = 55 if is_hp else 40
        self.rect(12, y, badge_w, 10, "F")

        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        self.set_xy(12, y + 1.5)
        self.cell(badge_w, 7, f"  {'⚠' if is_hp else '✔'}  {priority.upper()}", align="L")
        self.ln(14)

    def divider(self):
        self.set_draw_color(*SURFACE)
        self.set_line_width(0.5)
        self.line(12, self.get_y(), 198, self.get_y())
        self.ln(6)


# ── Main generation logic ─────────────────────────────────────────────────────
def generate_all():
    if not os.path.exists(EXCEL_FILE):
        print(f"❌  '{EXCEL_FILE}' not found. Make sure it is in the same folder.")
        return

    df = pd.read_excel(EXCEL_FILE)

    # Normalise column names (strip spaces, lower)
    df.columns = [c.strip() for c in df.columns]

    os.makedirs(REPORTS_DIR, exist_ok=True)
    count = 0

    for idx, row in df.iterrows():
        name   = str(row.get("Name",   "Unknown"))
        age    = int(row.get("Age",    0))
        email  = str(row.get("Email",  "N/A"))
        doctor = str(row.get("Doctor", "General"))
        date   = str(row.get("Date",   "N/A"))
        slot   = str(row.get("Slot",   "Morning"))

        # ── Smart priority logic ──────────────────────────────────────────
        priority = "High Priority" if (doctor == "Cardiologist" and age > 50) else "Normal"
        pid      = f"#PT-{idx + 1:04d}"

        # ── Build PDF ────────────────────────────────────────────────────
        pdf = CareReport(pid)
        pdf.set_auto_page_break(auto=True, margin=20)

        # Outer page background
        pdf.add_page()
        pdf.set_fill_color(*BG_DARK)
        pdf.rect(0, 0, 210, 297, "F")

        # ── Section 1: Patient Info ───────────────────────────────────────
        pdf.ln(4)
        pdf.section_title("Patient Information")
        pdf.kv_row("Patient ID",   pid,   highlight=False)
        pdf.kv_row("Full Name",    name,  highlight=True)
        pdf.kv_row("Age",          f"{age} years", highlight=False)
        pdf.kv_row("Email",        email, highlight=True)
        pdf.ln(4)

        # ── Section 2: Appointment Details ────────────────────────────────
        pdf.section_title("Appointment Details")
        pdf.kv_row("Specialist",   doctor, highlight=False)
        pdf.kv_row("Booked Date",  date,   highlight=True)
        pdf.kv_row("Time Slot",    slot,   highlight=False)
        pdf.ln(4)

        # ── Section 3: AI Priority Analysis ──────────────────────────────
        pdf.section_title("AI Priority Analysis")
        pdf.set_xy(12, pdf.get_y())
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*MUTED)
        reason = (
            "Age > 50 and Cardiologist – flagged for priority scheduling."
            if priority == "High Priority"
            else "Standard criteria met – normal queue placement."
        )
        pdf.set_fill_color(20, 30, 50)
        pdf.multi_cell(186, 6, f"  Automated Logic: {reason}",
                       fill=True)
        pdf.ln(4)
        pdf.priority_badge(priority)

        # ── Section 4: Status ─────────────────────────────────────────────
        pdf.section_title("RPA Execution Status")
        pdf.kv_row("Booking",      "Confirmed ✓", highlight=False)
        pdf.kv_row("Report",       "Auto-Generated by UiPath Bot", highlight=True)
        pdf.kv_row("Timestamp",
                   datetime.now().strftime("%d %b %Y  %H:%M:%S"),
                   highlight=False)
        pdf.ln(6)
        pdf.divider()

        # ── Disclaimer ────────────────────────────────────────────────────
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*MUTED)
        pdf.set_x(12)
        pdf.multi_cell(
            186, 5,
            "This report was automatically generated by the CareSync RPA "
            "Hospital Automation System. It is intended for administrative "
            "purposes only and does not constitute medical advice.",
        )

        # ── Save ──────────────────────────────────────────────────────────
        safe_name = name.replace(" ", "_")
        out_path  = os.path.join(REPORTS_DIR, f"{safe_name}_Medical_Report.pdf")
        pdf.output(out_path)
        print(f"  ✔  {out_path}")
        count += 1

    print(f"\n✅  {count} PDF report(s) generated inside '{REPORTS_DIR}/'")


if __name__ == "__main__":
    print("📄  CareSync PDF Report Generator (RPA Output)")
    print("──────────────────────────────────────────────")
    generate_all()
