# from fpdf import FPDF
# import csv

# def generate_pdf(csv_file):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=8)
    
#     with open(csv_file, 'r') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             pdf.cell(200, 10, txt=' | '.join(row), ln=True)

#     path = "temp/report.pdf"
#     pdf.output(path)
#     return path



from fpdf import FPDF

def generate_walk_pdf(start_time, end_time, map_image, pdf_path):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="Walk Tracker Report", ln=True, align='C')

    # Start and End time
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Start Time: {start_time}", ln=True)
    pdf.cell(200, 10, txt=f"End Time: {end_time}", ln=True)

    # Map Image
    pdf.ln(10)
    pdf.image(map_image, x=10, y=pdf.get_y(), w=190)

    # Output the PDF to the specified path
    pdf.output(pdf_path)

    return pdf_path
