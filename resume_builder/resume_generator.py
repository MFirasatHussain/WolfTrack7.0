from fpdf import FPDF
import os

class ResumeGenerator:
    def __init__(self, user_data):
        """
        Initializes the ResumeGenerator with user data.
        :param user_data: Dictionary containing resume details (name, email, phone, education, work_experience, skills).
        """
        self.user_data = user_data

    def generate_pdf(self, output_dir="generated_resumes", filename="resume.pdf"):
        """
        Generates a PDF resume.
        :param output_dir: Directory to save the generated PDF.
        :param filename: Name of the generated PDF file.
        :return: Path to the generated PDF file.
        """
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define the file path
        pdf_path = os.path.join(output_dir, filename)

        # Create the PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add Name
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(0, 10, txt=f"{self.user_data.get('name', 'Name Not Provided')}", ln=True, align="C")

        # Add Contact Details
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(0, 10, txt=f"Email: {self.user_data.get('email', 'Not Provided')}", ln=True)
        pdf.cell(0, 10, txt=f"Phone: {self.user_data.get('phone', 'Not Provided')}", ln=True)

        # Add Education Section
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, txt="Education", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=self.user_data.get('education', 'Not Provided'))

        # Add Work Experience Section
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, txt="Work Experience", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=self.user_data.get('work_experience', 'Not Provided'))

        # Add Skills Section
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, txt="Skills", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=self.user_data.get('skills', 'Not Provided'))

        # Save the PDF
        pdf.output(pdf_path)
        return pdf_path
