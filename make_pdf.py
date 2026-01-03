import sys
import os

print("------------------------------------------------")
print("[INFO] STEP 1: Importing PDF library...")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    print("   [OK] ReportLab loaded successfully.")
except ImportError:
    print("\n[ERROR] ReportLab is missing.")
    print("   [ACTION] Please run: pip install reportlab")
    sys.exit(1)

def create_test_pdf():
    file_name = "test_company_policy.pdf"
    
    print(f"\n[INFO] STEP 2: Creating file '{file_name}'...")
    try:
        c = canvas.Canvas(file_name, pagesize=letter)
        width, height = letter
        print("   [OK] Canvas initialized.")

        # --- Title ---
        print("   [INFO] Writing Title...")
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 50, "TechCorp Employee Handbook (2025)")
        
        # --- Section 1: Leave Policy ---
        print("   [INFO] Writing Section 1: Leave Policy...")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 100, "1. Leave Policy")
        
        c.setFont("Helvetica", 12)
        text = c.beginText(50, height - 120)
        text.setFont("Helvetica", 12)
        text.setLeading(15)
        
        lines = [
            "All full-time employees are eligible for the following leave categories:",
            "- Annual Leave: 25 days per year. (Must be used by Dec 31st).",
            "- Sick Leave: 10 days per year. (Requires medical certificate if > 2 days).",
            "- Casual Leave: 7 days. (Cannot be combined with Annual Leave).",
            "Note: Unused annual leave does not carry over to the next year."
        ]
        
        for line in lines:
            text.textLine(line)
        c.drawText(text)

        # --- Section 2: Remote Work ---
        print("   [INFO] Writing Section 2: Remote Work Policy...")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 250, "2. Remote Work Policy")
        
        text = c.beginText(50, height - 270)
        text.setFont("Helvetica", 12)
        text.setLeading(15)
        lines = [
            "Employees are allowed to Work from Home (WFH) for 2 days a week.",
            "The designated WFH days are Tuesday and Thursday.",
            "Core Collaboration Hours: All employees must be online between 10:00 AM and 4:00 PM.",
            "Employees must ensure they have a stable internet connection of at least 50 Mbps."
        ]
        for line in lines:
            text.textLine(line)
        c.drawText(text)

        # --- Section 3: Expense Policy ---
        print("   [INFO] Writing Section 3: Expense Policy...")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 400, "3. Travel & Expense Policy")
        
        text = c.beginText(50, height - 420)
        text.setFont("Helvetica", 12)
        text.setLeading(15)
        lines = [
            "Meal Allowance: Employees working past 9:00 PM can claim a dinner allowance of up to $30.",
            "Flight Travel: Economy class is mandatory for all flights under 6 hours.",
            "Team Outings: The budget for quarterly team outings is capped at $50 per head."
        ]
        for line in lines:
            text.textLine(line)
        c.drawText(text)

        # Save
        print("\n[INFO] STEP 3: Saving file...")
        c.save()
        print(f"   [SUCCESS] File saved as '{file_name}'")
        print("   [ACTION] Move this file to your 'data' folder and run ingest.py")
        print("------------------------------------------------")

    except Exception as e:
        print(f"\n[ERROR] Could not create PDF: {e}")

if __name__ == "__main__":
    create_test_pdf()