import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_sample_blood_report(output_filename="sample_blood_report.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E88E5'),
        alignment=1,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2C3E50'),
        alignment=1,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading3'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1565C0'),
        spaceBefore=15,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#333333')
    )

    elements = []

    # Title & Subtitle
    elements.append(Paragraph("METROPOLIS HEALTH DIAGNOSTICS", title_style))
    elements.append(Paragraph("Comprehensive Clinical Biochemistry & Hematology Report", subtitle_style))
    elements.append(Spacer(1, 10))

    # Patient Details Table
    patient_data = [
        [Paragraph("<b>Patient Name:</b> John Doe", body_style), Paragraph("<b>Age / Sex:</b> 45 Yrs / Male", body_style)],
        [Paragraph("<b>Referred By:</b> Dr. Sarah Jenkins, MD", body_style), Paragraph("<b>Date of Collection:</b> 2026-09-22", body_style)],
        [Paragraph("<b>Sample ID:</b> LAB-8894210", body_style), Paragraph("<b>Status:</b> Completed", body_style)]
    ]
    t_patient = Table(patient_data, colWidths=[270, 270])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F7FA')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_patient)
    elements.append(Spacer(1, 20))

    # Lab Test Results Table
    elements.append(Paragraph("Laboratory Test Findings", heading_style))
    
    test_data = [
        ["Test Description", "Observed Value", "Standard Unit", "Reference Interval", "Status Flag"],
        ["Fasting Blood Glucose", "118.5", "mg/dL", "70 - 99", "HIGH"],
        ["HbA1c (Glycated Hb)", "6.2", "%", "4.0 - 5.6", "HIGH"],
        ["Hemoglobin (Hb)", "14.2", "g/dL", "12.0 - 17.5", "NORMAL"],
        ["White Blood Cell Count (WBC)", "8.4", "x10^3 / µL", "4.5 - 11.0", "NORMAL"],
        ["Platelet Count", "260.0", "x10^3 / µL", "150 - 450", "NORMAL"],
        ["Total Cholesterol", "225.0", "mg/dL", "125 - 200", "HIGH"],
        ["HDL (Good) Cholesterol", "45.0", "mg/dL", "40 - 60", "NORMAL"],
        ["LDL (Bad) Cholesterol", "148.0", "mg/dL", "50 - 100", "HIGH"],
        ["Triglycerides", "165.0", "mg/dL", "35 - 150", "HIGH"],
        ["Thyroid Stimulating Hormone (TSH)", "2.4", "mIU/L", "0.4 - 4.0", "NORMAL"],
        ["Serum Creatinine", "0.95", "mg/dL", "0.6 - 1.2", "NORMAL"]
    ]

    t_tests = Table(test_data, colWidths=[160, 90, 80, 110, 100])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E88E5')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_tests)
    elements.append(Spacer(1, 25))

    # Pathologist Impression
    elements.append(Paragraph("Clinical Remarks & Impression", heading_style))
    impression_text = (
        "<b>Physician Impression:</b> Elevated fasting glucose and HbA1c indicative of impaired fasting glucose / pre-diabetic glycemic profile. "
        "Lipid panel shows mild hypercholesterolemia with elevated LDL and Triglycerides. Routine renal function and hematology indices are within normal limits. "
        "Dietary modifications, regular exercise, and follow-up medical consultation are advised."
    )
    elements.append(Paragraph(impression_text, body_style))
    elements.append(Spacer(1, 20))

    # Signatures & Disclaimer
    elements.append(Paragraph("<i>Electronically verified by Dr. R. K. Vance, MD (Senior Pathologist)</i>", body_style))

    doc.build(elements)
    print(f"Sample medical report generated: {output_filename}")
    return output_filename

if __name__ == "__main__":
    generate_sample_blood_report()