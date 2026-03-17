from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Safe-Surf AI Environment Test", ln=1, align='C')
pdf.output("env_test.pdf")
print("Environment Verified: PDF Engine is Operational.")