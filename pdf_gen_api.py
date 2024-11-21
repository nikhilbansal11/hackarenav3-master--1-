from flask import Flask, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
from PIL import Image

app = Flask(__name__)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    # Get the data from the request
    json_content = request.json['json_content']
    image = request.files['image']
    logo = request.files['logo']

    # Create the PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Add the header
    project_name = "Drlogy Imaging Center"
    project_description = "X-Ray | CT-Scan | MRI | USG"
    logo_image = Image(logo, 1*inch, 1*inch)
    logo_image.hAlign = 'RIGHT'
    header = Table([[Paragraph(project_name, styles["Heading1"]), logo_image]], colWidths=[4*inch, 2*inch])
    header_style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                              ('GRID', (0,0), (-1,-1), 1, colors.black),
                              ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                              ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                              ('FONTSIZE', (0,0), (-1,0), 14),
                              ('BOTTOMPADDING', (0,0), (-1,0), 12),
                              ('BACKGROUND', (0,0), (-1,0), colors.grey),
                              ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                              ('SPAN', (0,0), (0,0))])
    header.setStyle(header_style)

    # Add the patient information
    patient_name = json_content['patient_name']
    patient_id = json_content['patient_id']
    patient_address = json_content['patient_address']
    patient_contact = json_content['patient_contact']
    patient_info = [[Paragraph("Patient Name:", styles["BodyText"]), Paragraph(patient_name, styles["BodyText"])],
                    [Paragraph("Patient ID:", styles["BodyText"]), Paragraph(patient_id, styles["BodyText"])],
                    [Paragraph("Address:", styles["BodyText"]), Paragraph(patient_address, styles["BodyText"])],
                    [Paragraph("Contact:", styles["BodyText"]), Paragraph(patient_contact, styles["BodyText"])]]
    patient_info_table = Table(patient_info, colWidths=[2*inch, 4*inch])
    patient_info_style = TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black),
                                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                                    ('FONTSIZE', (0,0), (-1,-1), 10),
                                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                                    ('BACKGROUND', (0,0), (-1,0), colors.grey)])
    patient_info_table.setStyle(patient_info_style)

    # Add the medical information
    symptoms = json_content['symptoms']
    medical_terms = json_content['medical_terms']
    clinical_findings = json_content['clinical_findings']
    recommendations = json_content['recommendations']
    medical_info = [[Paragraph("Symptoms:", styles["BodyText"]), Paragraph(symptoms, styles["BodyText"])],
                    [Paragraph("Medical Terms:", styles["BodyText"]), Paragraph(medical_terms, styles["BodyText"])],
                    [Paragraph("Clinical Findings:", styles["BodyText"]), Paragraph(clinical_findings, styles["BodyText"])],
                    [Paragraph("Recommendations:", styles["BodyText"]), Paragraph(recommendations, styles["BodyText"])]]
    medical_info_table = Table(medical_info, colWidths=[2*inch, 4*inch])
    medical_info_style = TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black),
                                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                                    ('FONTSIZE', (0,0), (-1,-1), 10),
                                    ('BOTTOMPADDING', (0,0), (-1,-1), 6)])
    medical_info_table.setStyle(medical_info_style)

    # Assemble the report
    elements = [header, Spacer(1, 12),
                patient_info_table, Spacer(1, 12),
                medical_info_table]

    # Add the footer
    footer = Table([[Paragraph("Report created by Drlogy Imaging Center", styles["BodyText"])]], colWidths=[6*inch])
    footer_style = TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black),
                              ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                              ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                              ('FONTSIZE', (0,0), (-1,-1), 10),
                              ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                              ('BACKGROUND', (0,0), (-1,0), colors.grey)])
    footer.setStyle(footer_style)
    elements.append(footer)

    # Build the PDF
    doc.build(elements)

    # Return the PDF
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='medical_report.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)