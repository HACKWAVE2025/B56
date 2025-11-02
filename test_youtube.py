#!/usr/bin/env python3
"""
Test script to verify YouTube transcript extraction functionality
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from accessibility_hub.processing import youtube_processor

def test_youtube_processing():
    """Test YouTube processing with a sample educational video"""
    
    # Test URLs - using educational videos likely to have captions
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Simple test video
        "https://www.youtube.com/watch?v=3JdWlSF195Y",  # Khan Academy type video
        "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
    ]
    
    print("🧪 Testing YouTube Transcript Extraction")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📺 Test {i}: {url}")
        print("-" * 30)
        
        try:
            # Test the main processing function
            formatted_content, metadata, transcript_text = youtube_processor.process_youtube_video(url)
            
            print(f"✅ SUCCESS!")
            print(f"📝 Title: {metadata.get('title', 'Unknown')}")
            print(f"👤 Author: {metadata.get('author', 'Unknown')}")
            print(f"⏱️ Duration: {youtube_processor.format_duration(metadata.get('length'))}")
            print(f"📄 Transcript Length: {len(transcript_text)} characters")
            print(f"📊 Content Length: {len(formatted_content)} characters")
            
            # Show first 200 chars of transcript
            if transcript_text and len(transcript_text) > 50:
                preview = transcript_text[:200] + "..." if len(transcript_text) > 200 else transcript_text
                print(f"🔍 Transcript Preview: {preview}")
            else:
                print(f"⚠️ Limited/No transcript: {transcript_text[:100] if transcript_text else 'None'}")
            
            return True  # Success - stop testing more URLs
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            continue
    
    print(f"\n🔴 All test URLs failed. This might be due to:")
    print("   - Network restrictions (corporate firewall)")
    print("   - Geographic restrictions")  
    print("   - Videos not having captions")
    print("   - YouTube API access issues")
    
    return False

def test_direct_yt_dlp():
    """Test yt-dlp directly to check basic functionality"""
    
    print("\n🛠️ Testing yt-dlp directly")
    print("=" * 30)
    
    try:
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
        print(f"✅ yt-dlp working! Video title: {info.get('title', 'Unknown')}")
        print(f"📊 Available subtitles: {list(info.get('subtitles', {}).keys())}")
        print(f"🤖 Auto captions: {list(info.get('automatic_captions', {}).keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ yt-dlp failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 YouTube Processing Test Suite")
    print("================================")
    
    # Test 1: Direct yt-dlp functionality
    yt_dlp_works = test_direct_yt_dlp()
    
    # Test 2: Full YouTube processing pipeline
    if yt_dlp_works:
        youtube_works = test_youtube_processing()
        
        if youtube_works:
            print(f"\n🎉 OVERALL RESULT: YouTube processing is working!")
            print(f"✅ Your system can extract YouTube transcripts")
            print(f"🔧 The backend should work with YouTube URLs")
        else:
            print(f"\n⚠️ OVERALL RESULT: Issues with transcript extraction")
            print(f"🔧 yt-dlp works but video processing has problems")
    else:
        print(f"\n🔴 OVERALL RESULT: yt-dlp installation issue")
        print(f"🔧 Check your yt-dlp installation")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Try the working system with a document upload first")
    print(f"   2. Test YouTube with educational videos that have captions")
    print(f"   3. Check your network allows YouTube access")