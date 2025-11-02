#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, r'C:\accessibility-learning-hub\backend')

from accessibility_hub.processing import youtube_processor, tts_generator

def test_improved_tts():
    """Test the improved TTS with much shorter audio generation"""
    
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    print('🧪 Testing Improved TTS for YouTube...')
    print('=' * 50)
    
    try:
        # Get the YouTube content
        formatted_content, metadata, transcript_text = youtube_processor.process_youtube_video(url)
        
        print(f'📝 Video: {metadata.get("title", "Unknown")}')
        print(f'📄 Original transcript: {len(transcript_text)} characters')
        
        # Test the new clean speech extraction
        clean_speech = youtube_processor.extract_clean_speech_only(transcript_text)
        print(f'🎤 Clean speech only: {len(clean_speech)} characters ({len(clean_speech.split())} words)')
        
        if clean_speech:
            preview = clean_speech[:200] + '...' if len(clean_speech) > 200 else clean_speech
            print(f'🔍 Speech preview: {preview}')
            
            # Estimate audio length (rough: ~150 words per minute)
            word_count = len(clean_speech.split())
            estimated_minutes = word_count / 150
            print(f'⏱️ Estimated audio length: {estimated_minutes:.1f} minutes')
            
            if estimated_minutes > 5:
                print(f'⚠️ Still too long! Audio would be {estimated_minutes:.1f} minutes')
            else:
                print(f'✅ Perfect! Audio should be about {estimated_minutes:.1f} minutes')
        else:
            print('❌ No clean speech extracted')
            
    except Exception as e:
        print(f'❌ ERROR: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_improved_tts()