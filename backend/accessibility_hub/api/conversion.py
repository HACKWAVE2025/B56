import os
import uuid
from flask import request
from flask_restful import Resource
from accessibility_hub.processing import parser, simplifier, tts_generator

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

        try:
            # 1. Parse text
            raw_text, file_type = parser.extract_text(file_path)
            if "Unsupported" in raw_text:
                return {"message": f"Unsupported file type: {file_type}"}, 400

            # 2. Simplify text
            simplified_text = simplifier.simplify(raw_text)

            # 3. Save simplified result as HTML
            output_filename = f"{task_id}_simplified.html"
            output_path = os.path.join(upload_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                html_content = simplified_text.replace('\n\n', '</p><p>')
                f.write(f"<html><body><p>{html_content}</p></body></html>")
            
            # 4. Generate TTS Audio
            # Note: tts_generator.py uses the same relative path logic (temp_uploads)
            audio_filename = tts_generator.generate_tts_audio(simplified_text, task_id)

            print(f"Simplified HTML saved to: {output_path}")
            os.remove(file_path)

            return {
                "task_id": task_id,
                "status": "COMPLETED",
                # Flask will now serve these from the /api/result/ path automatically
                "simplified_file": output_filename, 
                "audio_file": audio_filename,
                "message": "File parsed, simplified, and saved."
            }, 200

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            print(f"Processing error: {e}")
            return {"message": f"Internal processing error: {e}"}, 500
