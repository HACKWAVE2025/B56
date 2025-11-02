#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, r'C:\accessibility-learning-hub\backend')

from accessibility_hub.processing import youtube_processor

def test_description_as_main_content():
    """Test YouTube processing with description as main content"""
    
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    print('🧪 Testing YouTube Description as Main Content...')
    print('=' * 60)
    
    try:
        # Get the YouTube content (now description-focused)
        formatted_content, metadata, description_content = youtube_processor.process_youtube_video(url)
        
        print(f'📝 Video: {metadata.get("title", "Unknown")}')
        print(f'👤 Author: {metadata.get("author", "Unknown")}')
        print(f'📄 Original description: {len(metadata.get("description", ""))} characters')
        print(f'🎯 Main content (cleaned description): {len(description_content)} characters')
        
        print(f'\n📋 Description Content Preview:')
        preview = description_content[:300] + '...' if len(description_content) > 300 else description_content
        print(f'"{preview}"')
        
        # Estimate TTS length
        word_count = len(description_content.split())
        estimated_minutes = word_count / 150  # ~150 words per minute
        print(f'\n⏱️ Estimated TTS audio length: {estimated_minutes:.1f} minutes')
        
        if estimated_minutes <= 3:
            print(f'✅ Perfect! Audio should be about {estimated_minutes:.1f} minutes')
        else:
            print(f'⚠️ Might be long: {estimated_minutes:.1f} minutes audio')
            
        print(f'\n🎯 RESULT: Now using video description as main content!')
        print(f'📖 Content will be: Description → Simplified Text → Audio')
        
    except Exception as e:
        print(f'❌ ERROR: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_description_as_main_content()