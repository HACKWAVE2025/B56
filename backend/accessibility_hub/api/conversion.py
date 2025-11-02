import os
import uuid
import json
from flask import request, send_file
from flask_restful import Resource
# Ensure 'exporter' is imported for file generation
from accessibility_hub.processing import parser, simplifier, tts_generator, math_linearizer, report_generator, exporter, youtube_processor 

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
        youtube_url = request.form.get('youtube_url')
        language = request.form.get('language', 'en') # Get language, default to English
        
        # Check if either file or YouTube URL is provided
        if not uploaded_file and not youtube_url:
            return {"message": "No file uploaded or YouTube URL provided."}, 400

        task_id = str(uuid.uuid4())
        upload_dir = get_upload_dir()
        
        # Handle file upload
        if uploaded_file:
            filename = f"{task_id}_{uploaded_file.filename}"
            file_path = os.path.join(upload_dir, filename)
            uploaded_file.save(file_path)
            
            # Use the new parser to get text and image data
            raw_text, image_data, file_type = parser.extract_text_and_images(file_path, task_id)
            
            if "Unsupported" in raw_text:
                os.remove(file_path)
                return {"message": f"Unsupported file type: {file_type}"}, 400
                
            # The original uploaded file is no longer needed after parsing
            os.remove(file_path)
            
        # Handle YouTube URL
        elif youtube_url:
            # Process YouTube video to extract description and metadata
            # Pass language for preferred subtitle extraction
            raw_text, video_metadata, description_content = youtube_processor.process_youtube_video(youtube_url, language=language)
            file_type = "youtube"
            image_data = [] # No images from YouTube URLs
            print(f"Successfully processed YouTube video: {video_metadata.get('title', 'Unknown Title')}")
            print(f"Using video description as main content: {len(description_content)} characters")

        audio_filename = None
        report_json = "{}"
        epub_filename = None 
        pdf_filename = None # State initialized for PDF filename

        try:
            # 1. Text and images are already extracted above
            
            # 2. Convert LaTeX to accessible MathML
            processed_text = math_linearizer.detect_and_convert_latex(raw_text)

            # 3. Simplify text (language-agnostic)
            simplified_text_with_headings = simplifier.simplify(processed_text)

            # 4. Translate simplified text to the target language
            translated_content = simplifier.translate_text(simplified_text_with_headings, target_lang=language)
            
            # If YouTube, also translate the description separately for TTS if it's different
            if file_type == "youtube":
                translated_description_for_tts = simplifier.translate_text(description_content, target_lang=language)
            else:
                translated_description_for_tts = translated_content

            # 5. Inject extracted images into the translated HTML content
            images_html = ""
            if image_data:
                for item in image_data:
                    img_src = f"/api/result/{item['filename']}" 
                    alt_text = item['alt_text']
                    images_html += f'<img src="{img_src}" alt="{alt_text}" style="max-width: 100%; height: auto; margin: 1rem 0;" />\n'

            simplified_html_content = translated_content + "\n" + images_html

            # 6. Generate Accessibility Report (on the translated content)
            report_json = report_generator.generate_report(translated_content, simplified_html_content, total_images=len(image_data))

            # 7. Save simplified (and translated) result as HTML
            output_filename = f"{task_id}_simplified.html"
            output_path = os.path.join(upload_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                final_html = simplified_html_content.replace('\n\n', '</p><p>')
                f.write(f"<html><body>{final_html}</body></html>")
            
            # 8. Generate TTS Audio from the translated text
            print(f"Generating TTS in '{language}' from translated content.")
            audio_filename = tts_generator.generate_tts_audio(translated_description_for_tts, task_id, language=language)
            
            # 9. Generate EPUB from translated content
            epub_filename = exporter.generate_epub(simplified_html_content, task_id)
            
            # 10. Generate PDF from translated content
            pdf_filename = exporter.generate_pdf(simplified_html_content, task_id)

            print(f"Simplified and translated HTML saved to: {output_path}")

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

class ServeFile(Resource):
    """Serves generated files (HTML, audio, etc.) for viewing/playback."""
    def get(self, filename):
        try:
            abs_file_path = os.path.join(get_serving_root_dir(), get_upload_dir(), filename)
            
            # Determine MIME type based on file extension
            if filename.endswith('.html'):
                mimetype = 'text/html'
            elif filename.endswith('.mp3'):
                mimetype = 'audio/mpeg'
            elif filename.endswith('.pdf'):
                mimetype = 'application/pdf'
            elif filename.endswith('.epub'):
                mimetype = 'application/epub+zip'
            else:
                mimetype = 'application/octet-stream'
            
            return send_file(
                abs_file_path,
                mimetype=mimetype,
                as_attachment=False  # Don't force download, allow viewing
            )
        except FileNotFoundError:
            print(f"File 404: File not found at {abs_file_path}")
            return {"message": "File not found."}, 404
        except Exception as e:
            print(f"Error serving file: {e}")
            return {"message": "Could not serve file."}, 500
