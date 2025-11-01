import os
from gtts import gTTS # NEW IMPORT
import uuid

TEMP_UPLOAD_FOLDER_NAME = 'temp_uploads'

def generate_tts_audio(text, task_id):
    """
    Generates and saves high-quality TTS audio using gTTS (Google Text-to-Speech).
    
    This library uses Google Translate's API, offering better voices 
    but relies on internet connectivity.
    """
    
    output_filename = f"{task_id}_audio.mp3"
    
    # Path is relative to the CWD (backend/ folder)
    output_path = os.path.join(TEMP_UPLOAD_FOLDER_NAME, output_filename)
    
    # We strip the text to ensure it's not empty, which can crash gTTS
    clean_text = text.strip()

    if not clean_text:
        print("Warning: TTS text was empty. Skipping audio generation.")
        return None

    try:
        # Initialize gTTS object
        tts = gTTS(text=clean_text, lang='en')
        
        # Save the audio file directly to the calculated path
        tts.save(output_path)
        
        print(f"TTS audio (gTTS) saved to: {output_path}")
        return output_filename
        
    except Exception as e:
        # Note: If there's no internet connection, this will fail.
        print(f"TTS generation error (gTTS): {e}")
        return None
