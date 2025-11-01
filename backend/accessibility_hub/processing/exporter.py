import os
import uuid
from ebooklib import epub
from html.parser import HTMLParser
import re
from reportlab.lib.pagesizes import letter # NEW IMPORT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer # NEW IMPORT
from reportlab.lib.styles import getSampleStyleSheet # NEW IMPORT
from reportlab.lib.colors import black, blue
from reportlab.lib.units import inch
from bs4 import BeautifulSoup # NEW IMPORT for parsing HTML structure

TEMP_UPLOAD_FOLDER_NAME = 'temp_uploads'

# Helper class to strip HTML tags for plain text in EPUB metadata
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    def handle_data(self, data):
        self.text.append(data)
    def get_data(self):
        return ''.join(self.text)

def get_serving_root_dir():
    # Returns the absolute path of the CWD (backend/)
    return os.getcwd() 

def generate_epub(simplified_html_content, task_id):
    """Generates an EPUB file from the simplified HTML content."""
    
    epub_filename = f"accessible_output_{task_id}.epub"
    epub_path = os.path.join(get_serving_root_dir(), TEMP_UPLOAD_FOLDER_NAME, epub_filename)
    
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier(task_id)
    book.set_title('Accessible Document')
    book.set_language('en')
    book.add_author('Accessibility Hub')
    
    # Extract body content (to avoid double wrapping the <html> tag)
    body_match = re.search(r'<body>(.*?)</body>', simplified_html_content, re.DOTALL)
    content_html = body_match.group(1).strip() if body_match else simplified_html_content
    
    # Create EPUB chapter
    c1 = epub.EpubHtml(title='Simplified Content', file_name='chap_01.xhtml', lang='en')
    
    # Apply clean HTML structure for EPUB:
    c1.content = f'<h1>Simplified Content</h1>{content_html}'
    
    book.add_item(c1)
    
    # --- FIX: Use book.spine and book.toc with list assignments ---
    book.toc = (epub.Link('chap_01.xhtml', 'Simplified Content', 'intro'), )
    book.spine = ['nav', c1] # 'nav' is reserved for the TOC file
    
    # Add minimal CSS for EPUB
    style = 'BODY { color: #333; } H1 { color: #4F46E5; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    try:
        epub.write_epub(epub_path, book, {})
        return epub_filename
    except Exception as e:
        print(f"EPUB Generation Error: {e}")
        return None

def generate_pdf(simplified_html_content, task_id):
    """Generates a PDF file from the simplified HTML content using ReportLab."""
    
    pdf_filename = f"accessible_output_{task_id}.pdf"
    pdf_path = os.path.join(get_serving_root_dir(), TEMP_UPLOAD_FOLDER_NAME, pdf_filename)
    
    try:
        doc = SimpleDocTemplate(
            pdf_path, 
            pagesize=letter,
            leftMargin=inch,
            rightMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        styles = getSampleStyleSheet()
        story = []
        
        # Use BeautifulSoup to parse the simplified HTML content
        soup = BeautifulSoup(simplified_html_content, 'html.parser')
        
        # --- PDF Rendering Logic ---
        
        # Define basic paragraph style
        P_STYLE = styles["Normal"]
        P_STYLE.leading = 16
        
        # Define heading style
        H2_STYLE = styles["h2"]
        H2_STYLE.textColor = blue
        H2_STYLE.spaceAfter = 12
        
        # Iterate over all top-level content elements (H2, P, Figure)
        for element in soup.find_all(['h2', 'p', 'figure']):
            text_content = element.get_text().strip()
            
            if not text_content:
                continue

            if element.name == 'h2':
                # Use Heading style for H2 tags
                story.append(Paragraph(text_content, H2_STYLE))
                story.append(Spacer(1, 0.2 * inch))
            
            elif element.name == 'p':
                # Use Normal style for Paragraphs
                story.append(Paragraph(text_content, P_STYLE))
            
            elif element.name == 'figure':
                # Handle the Image Placeholder (render its text description)
                caption = element.find('figcaption')
                alt_text = element.find('p', class_='text-xs')
                
                story.append(Spacer(1, 0.1 * inch))
                
                if caption:
                    story.append(Paragraph(f"--- Visual Element: {caption.get_text().strip()} ---", styles['Italic']))
                elif alt_text:
                    story.append(Paragraph(f"--- Visual Element: {alt_text.get_text().strip()} ---", styles['Italic']))
                
                story.append(Spacer(1, 0.1 * inch))

        # Build the document
        doc.build(story)
        return pdf_filename
        
    except Exception as e:
        print(f"PDF Generation Error (ReportLab): {e}")
        return None
