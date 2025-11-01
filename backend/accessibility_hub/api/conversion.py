import os
import uuid
import json
from flask import request, send_file
from flask_restful import Resource
# Ensure 'exporter' is imported for file generation
from accessibility_hub.processing import parser, simplifier, tts_generator, math_linearizer, report_generator, exporter 

TEMP_UPLOAD_FOLDER_NAME = 'temp_uploads'

# --- SIMPLIFIED PATH HELPERS ---
def get_upload_dir():
    """Returns the RELATIVE path to the temp_uploads folder, ensuring it exists."""
    full_path = TEMP_UPLOAD_FOLDER_NAME
    os.makedirs(full_path, exist_ok=True)
    return full_path

def get_serving_root_dir():
    return os.getcwd() 
# -----------------------------

class Upload(Resource):
    def post(self):
        uploaded_file = request.files.get('file')
        if not uploaded_file:
            return {"message": "No file uploaded."}, 400

        task_id = str(uuid.uuid4())
        upload_dir = get_upload_dir()
        filename = f"{task_id}_{uploaded_file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        uploaded_file.save(file_path)

        audio_filename = None
        report_json = "{}"
        epub_filename = None 
        pdf_filename = None # State initialized for PDF filename

        try:
            # 1. Parse text
            raw_text, file_type = parser.extract_text(file_path)
            if "Unsupported" in raw_text:
                os.remove(file_path)
                return {"message": f"Unsupported file type: {file_type}"}, 400
            
            # 2. LINEARIZE MATH 
            linearized_text = math_linearizer.detect_and_linearize(raw_text)

            # 3. Simplify text and get content with headings
            simplified_text_with_headings = simplifier.simplify(linearized_text)

            # 4. MOCK IMAGE DETECTION AND INSERTION
            image_placeholder_html = ""
            total_expected_images = 0
            
            if len(raw_text) > 1000:
                total_expected_images = 1 
                image_placeholder_html = simplifier.generate_image_html_placeholder(description="Complex Diagram (Fig 1.2)")
            
            simplified_html_content = simplified_text_with_headings
            if image_placeholder_html:
                 simplified_html_content += "\n\n" + image_placeholder_html 


            # 5. Generate Accessibility Report 
            report_json = report_generator.generate_report(simplified_text_with_headings, simplified_html_content, total_images=total_expected_images)

            # 6. Save simplified result as HTML for export pipeline input
            output_filename = f"{task_id}_simplified.html"
            output_path = os.path.join(upload_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                final_html = simplified_html_content.replace('\n\n', '</p><p>')
                f.write(f"<html><body>{final_html}</body></html>")
            
            # 7. Generate TTS Audio
            audio_filename = tts_generator.generate_tts_audio(simplified_text_with_headings, task_id)
            
            # 8. Generate EPUB
            epub_filename = exporter.generate_epub(simplified_html_content, task_id)
            
            # 9. Generate PDF (NEW INTEGRATION)
            pdf_filename = exporter.generate_pdf(simplified_html_content, task_id)

            print(f"Simplified HTML saved to: {output_path}")
            os.remove(file_path)

            return {
                "task_id": task_id,
                "status": "COMPLETED",
                "simplified_file": output_filename,
                "audio_file": audio_filename,
                "epub_file": epub_filename,
                "pdf_file": pdf_filename, # PDF filename included in response
                "report": report_json,
                "message": "MVP processing complete: Exports ready."
            }, 200

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            print(f"Processing error: {e}")
            return {"message": f"Internal processing error: {e}"}, 500

class DownloadEPUB(Resource):
    """Handles the download of generated EPUB files."""
    def get(self, filename):
        try:
            abs_file_path = os.path.join(get_serving_root_dir(), get_upload_dir(), filename)
            
            return send_file(
                abs_file_path,
                mimetype='application/epub+zip',
                as_attachment=True,
                download_name=filename
            )
        except FileNotFoundError:
            print(f"EPUB 404: File not found at {abs_file_path}")
            return {"message": "File not found."}, 404
        except Exception as e:
            print(f"Error serving EPUB: {e}")
            return {"message": "Could not serve file."}, 500
            
class DownloadPDF(Resource): # NEW RESOURCE
    """Handles the download of generated PDF files."""
    def get(self, filename):
        try:
            abs_file_path = os.path.join(get_serving_root_dir(), get_upload_dir(), filename)
            
            return send_file(
                abs_file_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        except FileNotFoundError:
            print(f"PDF 404: File not found at {abs_file_path}")
            return {"message": "File not found."}, 404
        except Exception as e:
            print(f"Error serving PDF: {e}")
            return {"message": "Could not serve file."}, 500
