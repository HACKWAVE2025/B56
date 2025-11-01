import pyttsx3
import os

# Use the relative path directly, as the conversion.py logic guarantees
# the CWD is the 'backend/' directory where this folder resides.
TEMP_UPLOAD_FOLDER_NAME = 'temp_uploads'

# --- SIMPLIFIED PATH HELPERS ---
def get_upload_dir():
    """Returns the RELATIVE path to the temp_uploads folder, ensuring it exists."""
    # This path is relative to the CWD (backend/)
    full_path = TEMP_UPLOAD_FOLDER_NAME
    os.makedirs(full_path, exist_ok=True)
    return full_path
# -------------------------------------------------------------

def generate_tts_audio(text, task_id):
    """Generates and saves TTS audio as an MP3 file."""
    
    upload_dir = get_upload_dir() # Use the simplified RELATIVE path
    output_filename = f"{task_id}_audio.mp3"
    # This path will be: temp_uploads/c018d6de-c04c-4e9c-901b-4c567fecb73d_audio.mp3
    output_path = os.path.join(upload_dir, output_filename)
    
    try:
        # NOTE: pyttsx3 depends on OS libraries (SAPI on Windows, eSpeak/TTS on Linux/Mac).
        # If this fails, it's an environment issue, but we still return the filename.
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait() 
        
        print(f"TTS audio saved to: {output_path}")
        return output_filename
        
    except Exception as e:
        print(f"FATAL TTS generation error (Check OS libs): {e}")
        # Return None if audio generation fails
        return None
