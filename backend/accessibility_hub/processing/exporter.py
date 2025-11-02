import os

TEMP_UPLOAD_FOLDER_NAME = 'temp_uploads'

def get_serving_root_dir():
    return os.getcwd() 

def generate_pdf(simplified_html_content, task_id):
    """PDF generation removed as per requirements"""
    return None

def generate_epub(simplified_html_content, task_id):
    """EPUB generation removed as per requirements"""
    return None