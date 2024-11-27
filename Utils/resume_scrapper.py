from PyPDF2 import PdfReader
import docx

def scrape_resume(file_path):
    """
    Extracts text content from a resume file.
    :param file_path: Path to the uploaded resume file.
    :return: Extracted text content.
    """
    if file_path.endswith('.pdf'):
        return scrape_pdf(file_path)
    elif file_path.endswith('.docx'):
        return scrape_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")

def scrape_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def scrape_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text
