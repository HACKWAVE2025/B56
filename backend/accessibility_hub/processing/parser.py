from PyPDF2 import PdfReader
from docx import Document # Requires python-docx
import os

def extract_pdf_text(file_path):
    """Extracts raw text from a PDF file."""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"PDF Parsing error: {e}")
        return None
    return text.strip()

def extract_docx_text(file_path):
    """Extracts raw text from a DOCX file."""
    text = []
    try:
        document = Document(file_path)
        for paragraph in document.paragraphs:
            # Preserve basic structure: treat each paragraph as a block
            text.append(paragraph.text)
    except Exception as e:
        print(f"DOCX Parsing error: {e}")
        return None
    # Join paragraphs with two newlines for readability/separation
    return '\n\n'.join(text).strip()

def extract_text(file_path):
    """Detects file type and calls the appropriate extractor."""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_pdf_text(file_path), "pdf"
    elif file_extension == '.docx':
        return extract_docx_text(file_path), "docx"
    else:
        # Handle other types if necessary, though MVP focuses on these
        return "Unsupported file type.", "unknown"