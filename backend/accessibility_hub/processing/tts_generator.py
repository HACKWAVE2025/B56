import os
import re
from gtts import gTTS # NEW IMPORT

TEMP_UPLOAD_FOLDER_NAME = 'temp_uploads'

def extract_clean_speech_text(text):
    """
    Extract only the actual spoken content for TTS, removing all metadata.
    This dramatically reduces audio length by focusing on speech content only.
    """
    if not text:
        return ""
    
    # Remove all JSON-like structures that cause long audio
    text = re.sub(r'\{[^}]*\}', '', text)           # Remove JSON objects
    text = re.sub(r'\[[^\]]*\]', '', text)          # Remove bracketed metadata
    text = re.sub(r'"[^"]*":', '', text)            # Remove JSON keys
    text = re.sub(r'[{}",]', ' ', text)             # Replace JSON syntax with spaces
    
    # Remove technical terms and metadata
    technical_terms = ['wireMagic', 'pb3', 'pens', 'wsWinStyles', 'wpWinPositions', 
                      'events', 'tStartMs', 'dDurationMs', 'segs', 'utf8']
    for term in technical_terms:
        text = re.sub(re.escape(term), '', text, flags=re.IGNORECASE)
    
    # Remove timestamps and numbers
    text = re.sub(r'\d+:\d+:\d+\.\d+', '', text)    # Timestamps
    text = re.sub(r'\d{4,}', '', text)              # Large numbers (likely timestamps)
    
    # Remove music and sound notations
    text = re.sub(r'♪+', '', text)                  # Music notes
    text = re.sub(r'\[.*?music.*?\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[.*?♪.*?\]', '', text)
    
    # Extract sentences (actual speech content)
    sentences = re.findall(r'[A-Z][^.!?]*[.!?]', text)
    if sentences:
        clean_text = ' '.join(sentences)
    else:
        # Fallback: extract word sequences
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        clean_text = ' '.join(words)
    
    # Final cleanup
    clean_text = re.sub(r'\s+', ' ', clean_text)
    clean_text = clean_text.strip()
    
    # Limit length for reasonable audio duration (max ~500 words)
    words = clean_text.split()
    if len(words) > 500:
        clean_text = ' '.join(words[:500])
        
    return clean_text

def generate_tts_audio(text, task_id, language='en'):
    """
    Generates a TTS audio file from the given text and saves it.
    Now accepts a language parameter for multilingual TTS.
    """
    if not text:
        print("TTS Generation: No text provided, skipping audio generation.")
        return None

    try:
        # Use the aggressive cleaning function to get only speech content
        clean_text = extract_clean_speech_text(text)
        
        if not clean_text:
            print("TTS Generation: No clean speech content found after filtering.")
            return None

        print(f"TTS Generation: Generating audio in '{language}' for text: '{clean_text[:100]}...'")

        # --- NEW: gTTS Integration ---
        tts = gTTS(text=clean_text, lang=language, slow=False)
        
        # Define output path
        upload_dir = os.path.join(os.getcwd(), TEMP_UPLOAD_FOLDER_NAME)
        os.makedirs(upload_dir, exist_ok=True)
        
        audio_filename = f"{task_id}_audio.mp3"
        audio_path = os.path.join(upload_dir, audio_filename)
        
        # Save the audio file
        tts.save(audio_path)
        
        print(f"TTS audio successfully generated and saved to {audio_path}")
        return audio_filename
        # --- END NEW ---

    except Exception as e:
        print(f"Error during TTS generation: {e}")
        return None
