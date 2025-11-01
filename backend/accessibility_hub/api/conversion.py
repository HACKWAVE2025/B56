import os
import uuid
from flask import request
from flask_restful import Resource
# ADDED report_generator
from accessibility_hub.processing import parser, simplifier, tts_generator, math_linearizer, report_generator 
import json # To parse the report string

TEMP_UPLOAD_FOLDER_NAME = 'temp_uploads'

# --- SIMPLIFIED PATH HELPERS ---
def get_upload_dir():
    """Returns the RELATIVE path to the temp_uploads folder, ensuring it exists."""
    full_path = TEMP_UPLOAD_FOLDER_NAME
    os.makedirs(full_path, exist_ok=True)
    return full_path
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
        report_json = "{}" # Initialize report JSON string

        try:
            # 1. Parse text
            raw_text, file_type = parser.extract_text(file_path)
            if "Unsupported" in raw_text:
                os.remove(file_path)
                return {"message": f"Unsupported file type: {file_type}"}, 400
            
            # 2. LINEARIZE MATH 
            linearized_text = math_linearizer.detect_and_linearize(raw_text)

            # 3. Simplify text
            simplified_text = simplifier.simplify(linearized_text)

            # 4. MOCK IMAGE DETECTION AND INSERTION
            # NOTE: We use the simplified text (without HTML) for TTS/report readability metrics
            image_placeholder_html = ""
            if len(raw_text) > 1000: 
                image_placeholder_html = simplifier.generate_image_html_placeholder(description="Complex Diagram (Fig 1.2)")
                # Append the HTML placeholder to the text that will be written to the file
                simplified_html_content = simplified_text + "\n\n" + image_placeholder_html 
            else:
                simplified_html_content = simplified_text

            # 5. Generate Accessibility Report (NEW STEP)
            # Report generator uses the simplified text (for metrics) and the HTML (for structure check)
            report_json = report_generator.generate_report(simplified_text, simplified_html_content)

            # 6. Save simplified result as HTML
            output_filename = f"{task_id}_simplified.html"
            output_path = os.path.join(upload_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                # Wrap simplified content in HTML structure, ensuring image placeholder is included
                final_html = simplified_html_content.replace('\n\n', '</p><p>')
                f.write(f"<html><body><p>{final_html}</p></body></html>")
            
            # 7. Generate TTS Audio
            audio_filename = tts_generator.generate_tts_audio(simplified_text, task_id)

            print(f"Simplified HTML saved to: {output_path}")
            os.remove(file_path)

            return {
                "task_id": task_id,
                "status": "COMPLETED",
                "simplified_file": output_filename,
                "audio_file": audio_filename,
                "report": report_json, # <-- FINAL REPORT INCLUDED HERE
                "message": "MVP processing complete: Report generated."
            }, 200

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            print(f"Processing error: {e}")
            return {"message": f"Internal processing error: {e}"}, 500

# NOTE: The ResultFile class is omitted as file serving is handled by Flask's static routes.
