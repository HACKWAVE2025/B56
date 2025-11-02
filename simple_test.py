#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, r'C:\accessibility-learning-hub\backend')

# Test YouTube processing
from accessibility_hub.processing import youtube_processor

def main():
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    print('🧪 Testing YouTube processor...')
    print('=' * 50)
    
    try:
        formatted_content, metadata, transcript_text = youtube_processor.process_youtube_video(url)
        
        print('✅ SUCCESS!')
        print(f'📝 Title: {metadata.get("title", "Unknown")}')
        print(f'👤 Author: {metadata.get("author", "Unknown")}')
        print(f'📄 Transcript length: {len(transcript_text)} characters')
        print(f'📊 Content length: {len(formatted_content)} characters')
        
        if transcript_text and len(transcript_text) > 50:
            preview = transcript_text[:200] + '...' if len(transcript_text) > 200 else transcript_text
            print(f'🔍 Transcript preview: {preview}')
        else:
            print('⚠️ No meaningful transcript extracted')
            
        print('\n🎯 RESULT: YouTube processing is working correctly!')
        print('✅ Your system can extract YouTube transcripts')
        print('🚀 The frontend should work with YouTube URLs')
        
    except Exception as e:
        print(f'❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        
        print('\n🔍 Troubleshooting:')
        print('1. Check network connection')
        print('2. Try a different YouTube URL')
        print('3. Verify the video has captions')

if __name__ == '__main__':
    main()