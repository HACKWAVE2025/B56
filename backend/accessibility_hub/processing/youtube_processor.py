"""
YouTube Video Processor
Handles extraction of video transcripts, metadata, and content processing for accessibility.
"""

import re
import yt_dlp
from urllib.parse import urlparse, parse_qs

def extract_video_id(youtube_url):
    """
    Extract video ID from various YouTube URL formats.
    """
    # Parse the URL
    parsed_url = urlparse(youtube_url)
    
    # Handle different YouTube URL formats
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    
    # If no valid video ID found
    raise ValueError("Invalid YouTube URL format")

def get_video_transcript_and_metadata(youtube_url, language='en'):
    """
    Get both transcript and metadata using yt-dlp, with language preference.
    """
    try:
        # Configure yt-dlp options
        # Prioritize the user-selected language for subtitles
        subtitle_langs = [language, 'en', 'en-US', 'en-GB']
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': subtitle_langs,
            'skip_download': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info
            info = ydl.extract_info(youtube_url, download=False)
            
            # Get metadata
            metadata = {
                'title': info.get('title', 'Unknown Title'),
                'description': info.get('description', 'No description available')[:1000],  # Limit length
                'author': info.get('uploader', 'Unknown'),
                'length': info.get('duration', None),
                'views': info.get('view_count', None),
                'publish_date': info.get('upload_date', None)
            }
            
            # Try to get subtitles
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            transcript_text = ""
            transcript_source = "none"
            
            # Priority: Manual subtitles > Automatic captions
            # The user's selected language is now first in the list
            
            # Try manual subtitles first
            for lang in subtitle_langs:
                if lang in subtitles:
                    try:
                        # Download and extract subtitle content
                        subtitle_url = subtitles[lang][0]['url']
                        transcript_text = download_and_parse_subtitles(subtitle_url)
                        transcript_source = f"manual subtitles ({lang})"
                        break
                    except Exception as e:
                        print(f"Failed to download manual subtitles for {lang}: {e}")
                        continue
            
            # If no manual subtitles, try automatic captions
            if not transcript_text:
                for lang in subtitle_langs:
                    if lang in automatic_captions:
                        try:
                            subtitle_url = automatic_captions[lang][0]['url']
                            transcript_text = download_and_parse_subtitles(subtitle_url)
                            transcript_source = f"automatic captions ({lang})"
                            break
                        except Exception as e:
                            print(f"Failed to download automatic captions for {lang}: {e}")
                            continue
            
            if transcript_text:
                print(f"Successfully extracted transcript from {transcript_source}: {len(transcript_text)} characters")
                return transcript_text, metadata, transcript_source
            else:
                # No subtitles available
                fallback_text = ("No subtitles or captions are available for this video. "
                               "This could be because: 1) The creator hasn't added captions, "
                               "2) Auto-captions are disabled, 3) The video language isn't supported. "
                               "Try finding educational videos that specifically mention having captions/subtitles.")
                return fallback_text, metadata, "no subtitles"
                
    except Exception as e:
        print(f"Error extracting video info: {e}")
        # Fallback metadata
        try:
            video_id = extract_video_id(youtube_url)
        except Exception:
            video_id = "unknown"
            
        fallback_metadata = {
            'title': f'YouTube Video (ID: {video_id})',
            'description': f'Could not extract video information. Error: {str(e)}',
            'author': 'Unknown',
            'length': None,
            'views': None,
            'publish_date': None
        }
        
        fallback_text = f"Could not process this YouTube video. Error details: {str(e)}"
        
        return fallback_text, fallback_metadata, "error"

def download_and_parse_subtitles(subtitle_url):
    """
    Download subtitle file and extract text content.
    """
    import urllib.request
    import xml.etree.ElementTree as ET
    
    try:
        # Download subtitle content
        with urllib.request.urlopen(subtitle_url) as response:
            subtitle_content = response.read().decode('utf-8')
        
        # Parse based on format (usually XML for YouTube)
        if subtitle_content.strip().startswith('<?xml') or '<transcript>' in subtitle_content:
            # Parse XML format
            root = ET.fromstring(subtitle_content)
            texts = []
            
            # Handle different XML formats
            for text_elem in root.findall('.//text'):
                text_content = text_elem.text
                if text_content:
                    texts.append(text_content.strip())
            
            # Join all text segments
            full_text = ' '.join(texts)
            
            # Clean up the text
            full_text = clean_transcript_text(full_text)
            
            return full_text
            
        else:
            # If it's not XML, try to use it as plain text
            return clean_transcript_text(subtitle_content)
            
    except Exception as e:
        print(f"Error downloading/parsing subtitles: {e}")
        raise e

def clean_transcript_text(text):
    """
    Clean and format transcript text for better readability and TTS.
    """
    if not text:
        return ""
    
    # Remove HTML entities
    import html
    text = html.unescape(text)
    
    # Remove JSON-like structures and metadata that were causing long audio
    text = re.sub(r'\{[^}]*\}', '', text)  # Remove JSON objects
    text = re.sub(r'\[[^\]]*\]', '', text)  # Remove bracketed content like [♪♪♪]
    text = re.sub(r'"[^"]*":', '', text)    # Remove JSON keys
    text = re.sub(r'[{}",]', '', text)      # Remove JSON syntax characters
    
    # Remove timestamps and technical markers
    text = re.sub(r'\d+:\d+:\d+\.\d+', '', text)     # Remove timestamps
    text = re.sub(r'tStartMs|dDurationMs|segs|utf8', '', text)  # Remove technical terms
    text = re.sub(r'<[^>]+>', '', text)               # Remove HTML tags
    text = re.sub(r'&[a-zA-Z]+;', '', text)          # Remove HTML entities
    
    # Remove music and sound notation
    text = re.sub(r'♪+', '', text)                   # Remove music notes
    text = re.sub(r'\[.*?music.*?\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[.*?♪.*?\]', '', text)
    
    # Clean up whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    
    # Fix punctuation spacing
    text = re.sub(r'\s+([,.!?])', r'\1', text)       # Fix spacing before punctuation
    text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Ensure space after sentences
    
    # Remove any remaining non-speech content
    text = re.sub(r'^[^a-zA-Z]*', '', text)          # Remove leading non-letters
    text = re.sub(r'[^a-zA-Z]*$', '', text)          # Remove trailing non-letters
    
    return text.strip()

def extract_clean_speech_only(transcript_text):
    """
    Extract only the spoken words from transcript for TTS, removing all technical metadata.
    This creates much shorter, focused audio.
    """
    if not transcript_text:
        return ""
    
    # Apply the same cleaning as in TTS generator
    clean_text = clean_transcript_text(transcript_text)
    
    # Extract only actual speech sentences
    sentences = re.findall(r'[A-Z][^.!?]*[.!?]', clean_text)
    if sentences:
        speech_only = ' '.join(sentences)
    else:
        # Fallback: extract word sequences
        words = re.findall(r'\b[a-zA-Z]+\b', clean_text)
        speech_only = ' '.join(words)
    
    # Limit to reasonable length for audio
    words = speech_only.split()
    if len(words) > 300:  # About 2-3 minutes of speech
        speech_only = ' '.join(words[:300]) + "."
    
    return speech_only.strip()

def process_youtube_video(youtube_url, language='en'):
    """
    Main function to process a YouTube video.
    It now accepts a language parameter to pass to the metadata extractor.
    """
    try:
        # Get transcript and metadata with language preference
        transcript, metadata, source = get_video_transcript_and_metadata(youtube_url, language=language)
        
        # The main content is now the video's description
        description_content = extract_description_content(metadata.get('description', ''))
        
        if not description_content:
            print("Warning: YouTube video description was empty. Falling back to transcript.")
            # Fallback to cleaned transcript if description is empty
            main_content = extract_clean_speech_only(transcript)
        else:
            main_content = description_content

        return main_content, metadata, description_content

    except Exception as e:
        print(f"An error occurred in process_youtube_video: {e}")
        # Return empty strings and a placeholder metadata object on failure
        return "", {"title": "Error Processing Video", "description": str(e)}, ""

# --- CONTENT EXTRACTION AND CLEANING ---

def extract_description_content(description):
    """
    Extract and clean the video description to use as main content.
    This prioritizes the description over transcript for processing.
    """
    if not description:
        return "No description available for this video."
    
    # Clean the description
    clean_desc = description.strip()
    
    # Remove URLs
    clean_desc = re.sub(r'http[s]?://\S+', '', clean_desc)
    clean_desc = re.sub(r'www\.\S+', '', clean_desc)
    
    # Remove excessive newlines
    clean_desc = re.sub(r'\n{3,}', '\n\n', clean_desc)
    
    # Remove social media handles and hashtags if excessive
    clean_desc = re.sub(r'#\w+', '', clean_desc)
    clean_desc = re.sub(r'@\w+', '', clean_desc)
    
    # Clean up spacing
    clean_desc = re.sub(r'\s+', ' ', clean_desc)
    
    # If description is very short, add context
    if len(clean_desc.strip()) < 50:
        clean_desc = f"Video Description: {clean_desc}\n\nThis video may contain visual or audio content that is not fully described in the text description."
    
    return clean_desc.strip()

def format_duration(seconds):
    """Convert seconds to readable duration format."""
    if not seconds:
        return "Unknown duration"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def format_number(num):
    """Format large numbers with commas."""
    if not num:
        return "Unknown"
    return f"{num:,}"

def format_date(date_str):
    """Format date string."""
    if not date_str:
        return "Unknown"
    
    # yt-dlp returns dates in YYYYMMDD format
    if len(date_str) == 8:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}-{month}-{day}"
    
    return str(date_str)

def clean_description(description):
    """Clean and format video description."""
    if not description:
        return "No description available."
    
    # Limit description length for processing
    if len(description) > 1000:
        description = description[:1000] + "..."
    
    # Remove excessive newlines and clean up
    description = re.sub(r'\n{3,}', '\n\n', description)
    return description.strip()