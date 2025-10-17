"""YouTube video processor for extracting transcripts and generating documentation."""

import asyncio
import re
from typing import Optional, Tuple, Dict, Any

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    YouTubeTranscriptApi = None
    TextFormatter = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from pytube import YouTube
except ImportError:
    YouTube = None


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in youtube_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Invalid YouTube URL")


async def get_video_info(video_id: str, url: str) -> Dict[str, Any]:
    """Extract video information using yt-dlp or pytube."""
    
    # Try yt-dlp first
    if yt_dlp:
        try:
            def extract_info():
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    return {
                        "title": info.get('title', 'Unknown Title'),
                        "description": info.get('description', ''),
                        "duration": info.get('duration', 0),
                        "view_count": info.get('view_count'),
                        "channel": info.get('uploader', 'Unknown Channel'),
                        "upload_date": info.get('upload_date'),
                        "url": url,
                        "video_id": video_id,
                    }
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, extract_info)
        except Exception as e:
            print(f"yt-dlp failed: {e}")
    
    # Fallback to pytube
    if YouTube:
        try:
            def extract_info():
                yt = YouTube(url)
                return {
                    "title": yt.title,
                    "description": yt.description,
                    "duration": yt.length,
                    "view_count": yt.views,
                    "channel": yt.author,
                    "upload_date": yt.publish_date.strftime('%Y%m%d') if yt.publish_date else None,
                    "url": url,
                    "video_id": yt.video_id,
                }
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, extract_info)
        except Exception as e:
            print(f"pytube failed: {e}")
    
    # Return minimal info if both fail
    return {
        "title": f"Video {video_id}",
        "description": "Description not available",
        "duration": 0,
        "view_count": None,
        "channel": "Unknown Channel",
        "upload_date": None,
        "url": url,
        "video_id": video_id,
    }


async def get_transcript(video_id: str, language: str = "en") -> Optional[str]:
    """Extract video transcript using YouTube Transcript API."""
    
    if not YouTubeTranscriptApi or not TextFormatter:
        return None
    
    def extract_transcript():
        try:
            text_formatter = TextFormatter()
            
            # Try to get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try manual transcript first, then auto-generated
            transcript = None
            try:
                transcript = transcript_list.find_manually_created_transcript([language])
            except:
                try:
                    transcript = transcript_list.find_generated_transcript([language])
                except:
                    # Get first available transcript
                    for t in transcript_list:
                        transcript = t
                        break
            
            if not transcript:
                return None
            
            # Fetch and format
            fetched = transcript.fetch()
            return text_formatter.format_transcript(fetched)
            
        except Exception as e:
            print(f"Transcript extraction failed: {e}")
            return None
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extract_transcript)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs}s"


def estimate_tokens(text: str) -> int:
    """Estimate token count for text content."""
    try:
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(text))
    except:
        # Fallback: approximately 4 characters per token
        return len(text) // 4


def generate_documentation(video_info: Dict[str, Any], transcript: Optional[str]) -> str:
    """Generate markdown documentation from video information and transcript."""
    
    doc_parts = []
    
    # Header
    doc_parts.append("# YouTube Video Documentation\n\n")
    doc_parts.append(f"**Title:** {video_info.get('title', 'Unknown')}\n\n")
    doc_parts.append(f"**URL:** {video_info.get('url', 'Unknown')}\n\n")
    doc_parts.append(f"**Duration:** {format_duration(video_info.get('duration', 0))}\n\n")
    doc_parts.append(f"**Views:** {video_info.get('view_count', 'Unknown'):,}\n\n" if video_info.get('view_count') else "**Views:** Unknown\n\n")
    doc_parts.append(f"**Channel:** {video_info.get('channel', 'Unknown')}\n\n")
    
    if video_info.get('upload_date'):
        doc_parts.append(f"**Upload Date:** {video_info.get('upload_date')}\n\n")
    
    doc_parts.append("---\n\n")
    
    # Description
    if video_info.get('description'):
        doc_parts.append("## Description\n\n")
        doc_parts.append(f"{video_info['description']}\n\n")
    
    # Transcript
    if transcript:
        doc_parts.append("## Transcript\n\n")
        doc_parts.append(f"{transcript}\n\n")
    else:
        doc_parts.append("## Transcript\n\n")
        doc_parts.append("*Transcript not available for this video.*\n\n")
    
    # Token estimation
    content = "".join(doc_parts)
    estimated_tokens = estimate_tokens(content)
    doc_parts.append("---\n\n")
    doc_parts.append(f"**Estimated Tokens:** {estimated_tokens:,}\n")
    
    return "".join(doc_parts)


async def process_youtube_video(url: str) -> Tuple[Dict[str, Any], str]:
    """Process a YouTube video and return info and documentation."""
    
    # Extract video ID
    video_id = extract_video_id(url)
    
    # Get video information
    video_info = await get_video_info(video_id, url)
    
    # Get transcript
    transcript = await get_transcript(video_id)
    
    # Generate documentation
    documentation = generate_documentation(video_info, transcript)
    
    return video_info, documentation