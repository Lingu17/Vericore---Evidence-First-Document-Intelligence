"""
Sample Business Document Generator for NovaTech.
Generates realistic multi-page PDF and TXT test documents with structured sections,
page counts, and policies for demoing DocuPilot RAG retrieval.
"""

from pathlib import Path
import pymupdf as fitz


def create_handbook_pdf(output_path: Path):
    doc = fitz.open()

    # Page 1: Welcome & Code of Conduct
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 70), "NOVATECH ENTERPRISES", fontsize=18, fontname="helv", color=(0.1, 0.2, 0.4))
    page1.insert_text((50, 95), "Employee Handbook & Workplace Guidelines (v2025)", fontsize=12, fontname="helv", color=(0.3, 0.3, 0.3))

    text_p1 = """1. WELCOME TO NOVATECH
Welcome to NovaTech. We are committed to fostering an innovative, inclusive, and high-performance culture. This handbook outlines key policies, working standards, and mutual expectations for all full-time and part-time staff members.

2. EQUAL OPPORTUNITY & NON-DISCRIMINATION
NovaTech provides equal employment opportunities to all applicants and team members regardless of race, religion, gender, sexual orientation, disability, or veteran status. Harassment of any nature is strictly prohibited and subject to immediate disciplinary investigation.

3. WORKPLACE CODE OF CONDUCT
Employees are expected to act with honesty, integrity, and professionalism in all business dealings. Confidential company data, customer records, and internal technical documentation must be safeguarded at all times in compliance with our information security protocols."""

    page1.insert_textbox(fitz.Rect(50, 120, 545, 750), text_p1, fontsize=10, fontname="helv")
    page1.insert_text((50, 800), "NovaTech Employee Handbook - Page 1", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    # Page 2: Working Hours & Probation
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 70), "NOVATECH ENTERPRISES - EMPLOYMENT POLICIES", fontsize=14, fontname="helv", color=(0.1, 0.2, 0.4))

    text_p2 = """4. PROBATIONARY PERIOD
All new full-time employees undergo a mandatory probationary period of 90 calendar days from their official start date. During this time, direct supervisors conduct bi-weekly check-ins to review progress, align on KPIs, and assess overall culture fit. Upon successful completion of the 90-day period, permanent employment status is officially confirmed.

5. WORKING HOURS & HYBRID WORK SCHEDULE
NovaTech operates on a 40-hour standard work week. Standard business hours are 9:00 AM to 5:00 PM local time, Monday through Friday. We support a flexible hybrid work model allowing up to 3 remote work days per week, provided core team meetings between 10:00 AM and 3:00 PM are attended.

6. PERFORMANCE EVALUATIONS & REVIEWS
Formal performance appraisals are conducted bi-annually in June and December. Reviews evaluate role-based deliverables, leadership values, and milestone achievements. Merit-based salary adjustments and promotional evaluations occur following the year-end December review cycle."""

    page2.insert_textbox(fitz.Rect(50, 100, 545, 750), text_p2, fontsize=10, fontname="helv")
    page2.insert_text((50, 800), "NovaTech Employee Handbook - Page 2", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    # Page 3: Security & Termination
    page3 = doc.new_page(width=595, height=842)
    page3.insert_text((50, 70), "NOVATECH ENTERPRISES - SEPARATION & COMPLIANCE", fontsize=14, fontname="helv", color=(0.1, 0.2, 0.4))

    text_p3 = """7. INFORMATION SECURITY & DEVICE USAGE
Company-issued laptops and mobile devices must utilize multi-factor authentication (MFA) and encrypted storage. Installation of unauthorized third-party software or unapproved cloud storage services is prohibited.

8. RESIGNATION AND NOTICE PERIOD
Employees wishing to resign must submit written notice to their department manager and HR. The standard notice period for regular full-time staff is 30 calendar days. Executive and senior managerial roles require a 60-day notice period unless an alternative arrangement is mutually approved in writing."""

    page3.insert_textbox(fitz.Rect(50, 100, 545, 750), text_p3, fontsize=10, fontname="helv")
    page3.insert_text((50, 800), "NovaTech Employee Handbook - Page 3", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    doc.save(str(output_path))
    doc.close()
    print(f"Created: {output_path}")


def create_leave_policy_pdf(output_path: Path):
    doc = fitz.open()

    # Page 1: Annual Leave & Carry Forward
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 70), "NOVATECH TIME-OFF & LEAVE POLICY", fontsize=18, fontname="helv", color=(0.1, 0.2, 0.4))
    page1.insert_text((50, 95), "Comprehensive Leave Regulations (Ref: HR-POL-2025-04)", fontsize=12, fontname="helv", color=(0.3, 0.3, 0.3))

    text_p1 = """1. ANNUAL LEAVE ENTITLEMENT
All permanent full-time employees are entitled to 24 annual leave days per calendar year, accrued at a rate of 2.0 days per completed month of active service. New joiners begin accruing leave immediately upon their first day of employment and may request leave following 30 days of service.

2. CARRY-FORWARD OF UNUSED LEAVE
Employees are encouraged to utilize their full annual leave allocation during each calendar year. However, employees may carry forward a maximum of up to 8 unused annual leave days into the following calendar year. Any carried-forward leave days must be utilized before March 31st (Q1) of the subsequent year, after which they will lapse automatically. Unused leave beyond the 8-day cap is not eligible for cash encashment.

3. LEAVE APPLICATION & APPROVAL PROCESS
Leave requests exceeding 3 consecutive business days must be submitted through the HR portal at least two weeks in advance. Department managers must approve or reject leave requests within 3 business days."""

    page1.insert_textbox(fitz.Rect(50, 120, 545, 750), text_p1, fontsize=10, fontname="helv")
    page1.insert_text((50, 800), "NovaTech Leave Policy - Page 1", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    # Page 2: Sick & Parental Leave
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 70), "NOVATECH TIME-OFF & LEAVE POLICY - SPECIAL LEAVE", fontsize=14, fontname="helv", color=(0.1, 0.2, 0.4))

    text_p2 = """4. SICK AND MEDICAL LEAVE
Employees are granted 10 paid sick leave days per calendar year for personal illness, medical appointments, or family medical care. Absences exceeding two consecutive working days require a formal medical certificate issued by a licensed physician.

5. PARENTAL AND MATERNITY LEAVE
NovaTech provides 16 weeks of fully paid maternity leave for primary caregivers following childbirth or adoption. Secondary caregivers and non-birthing parents receive 6 weeks of fully paid paternity leave. Parental leave may be scheduled flexibly across the child's first 12 months.

6. BEREAVEMENT AND COMPASSIONATE LEAVE
Employees are eligible for up to 5 days of paid bereavement leave in the event of the loss of an immediate family member (spouse, child, parent, sibling). Additional unpaid compassionate leave may be granted upon request."""

    page2.insert_textbox(fitz.Rect(50, 100, 545, 750), text_p2, fontsize=10, fontname="helv")
    page2.insert_text((50, 800), "NovaTech Leave Policy - Page 2", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    doc.save(str(output_path))
    doc.close()
    print(f"Created: {output_path}")


def create_benefits_policy_pdf(output_path: Path):
    doc = fitz.open()

    # Page 1: Health, Insurance, and Retirement
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 70), "NOVATECH TOTAL REWARDS & BENEFITS", fontsize=18, fontname="helv", color=(0.1, 0.2, 0.4))
    page1.insert_text((50, 95), "Employee Benefits Guide & Coverage Summary (2025)", fontsize=12, fontname="helv", color=(0.3, 0.3, 0.3))

    text_p1 = """1. HEALTH & MEDICAL INSURANCE COVERAGE
NovaTech provides comprehensive group medical, dental, and vision insurance coverage for all permanent full-time employees and their eligible dependents.
- Medical Coverage: Up to $500,000 maximum lifetime benefit coverage per enrolled member.
- Coverage Start Date: Effective immediately on Day 1 of employment with zero waiting period.
- Premium Share: The company covers 100% of the employee premium and 80% for enrolled family dependents.
- Prescription Drugs: 90% co-pay covered for generic and formulary medications.

2. RETIREMENT & 401(K) SAVINGS PLAN
Eligible staff may participate in the NovaTech 401(k) Retirement Plan. NovaTech matches 100% of employee contributions up to 5% of gross base salary. Company matching contributions vest immediately at 100%."""

    page1.insert_textbox(fitz.Rect(50, 120, 545, 750), text_p1, fontsize=10, fontname="helv")
    page1.insert_text((50, 800), "NovaTech Benefits Policy - Page 1", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    # Page 2: Wellness, Stipends & Perks
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 70), "NOVATECH TOTAL REWARDS & BENEFITS - WELLNESS & STIPENDS", fontsize=14, fontname="helv", color=(0.1, 0.2, 0.4))

    text_p2 = """3. LEARNING AND PROFESSIONAL DEVELOPMENT STIPEND
To promote continuous skill development, every employee receives an annual learning stipend of $1,500 per calendar year. This stipend covers certified courses, professional conferences, academic books, and industry examination fees. Expenses must be pre-approved by the team lead via the expensing portal.

4. WELLNESS & FITNESS REIMBURSEMENT
NovaTech reimburses up to $50 per month ($600 annually) for qualified wellness activities, including gym memberships, fitness classes, mental health app subscriptions (e.g. Headspace/Calm), and home fitness equipment.

5. COMMUTER AND MEAL ALLOWANCES
Employees working on-site at regional headquarters receive a subsidized transit pass and a daily catered lunch allowance of $15 per active in-office working day."""

    page2.insert_textbox(fitz.Rect(50, 100, 545, 750), text_p2, fontsize=10, fontname="helv")
    page2.insert_text((50, 800), "NovaTech Benefits Policy - Page 2", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

    doc.save(str(output_path))
    doc.close()
    print(f"Created: {output_path}")


def main():
    out_dir = Path(__file__).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    create_handbook_pdf(out_dir / "NovaTech_Employee_Handbook.pdf")
    create_leave_policy_pdf(out_dir / "NovaTech_Leave_Policy.pdf")
    create_benefits_policy_pdf(out_dir / "NovaTech_Benefits_Policy.pdf")
    print("All sample documents successfully regenerated!")


if __name__ == "__main__":
    main()
