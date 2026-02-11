from io import BytesIO
from pypdf import PdfReader


def extract_text_from_pdf(pdf_file):
    """Extract all text content from an uploaded PDF file."""
    reader = PdfReader(BytesIO(pdf_file.read()))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()