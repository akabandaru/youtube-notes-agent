import re
import math
from typing import Dict, Any, List, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp

class YouTubeExtractor:
    """
    Utility class to extract YouTube video ID, metadata, and time-coded transcript.
    """
    
    @staticmethod
    def extract_video_id(url_or_id: str) -> str:
        """
        Extracts 11-character YouTube video ID from various URL formats or raw ID string.
        
        Supported formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - VIDEO_ID (raw 11 chars)
        """
        url_or_id = url_or_id.strip()
        
        # Regular expression covering standard YouTube URLs
        patterns = [
            r'(?:v=|\/embed\/|\/shorts\/|\/v\/|https?:\/\/youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
                
        raise ValueError(f"Invalid YouTube URL or Video ID: '{url_or_id}'. Could not parse video ID.")

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """
        Formats seconds float into readable [MM:SS] or [HH:MM:SS] string.
        """
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    @classmethod
    def get_transcript(cls, video_id: str) -> List[Dict[str, Any]]:
        """
        Fetches transcript entries for a video ID using youtube-transcript-api.
        Returns a list of dicts with 'text', 'start', 'duration', and 'timestamp_str'.
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 1. Try manually created English transcripts
            try:
                transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
            except NoTranscriptFound:
                # 2. Try generated English transcripts
                try:
                    transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
                except NoTranscriptFound:
                    # 3. Fallback: Take first available transcript and translate to English
                    first_transcript = next(iter(transcript_list))
                    transcript = first_transcript.translate('en')
                    
            raw_data = transcript.fetch()
            
            # Enrich entries with formatted timestamp string
            formatted_transcript = []
            for item in raw_data:
                formatted_transcript.append({
                    "text": item.get("text", "").strip(),
                    "start": item.get("start", 0.0),
                    "duration": item.get("duration", 0.0),
                    "timestamp_str": cls.format_timestamp(item.get("start", 0.0))
                })
                
            return formatted_transcript

        except TranscriptsDisabled:
            raise RuntimeError("Transcripts are disabled for this YouTube video.")
        except NoTranscriptFound:
            raise RuntimeError("No transcript or subtitles could be found for this video.")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch transcript: {str(e)}")

    @classmethod
    def get_metadata(cls, video_url_or_id: str) -> Dict[str, Any]:
        """
        Fetches video metadata (title, channel, duration, thumbnail, description) using yt-dlp.
        """
        video_id = cls.extract_video_id(video_url_or_id)
        full_url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': False,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(full_url, download=False)
                return {
                    "video_id": video_id,
                    "url": full_url,
                    "title": info.get("title", "Untitled Video"),
                    "channel": info.get("uploader") or info.get("channel", "Unknown Channel"),
                    "duration_seconds": info.get("duration", 0),
                    "duration_str": cls.format_timestamp(info.get("duration", 0)),
                    "thumbnail_url": info.get("thumbnail", f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"),
                    "description": info.get("description", "")[:500]  # First 500 chars snippet
                }
        except Exception as e:
            # Fallback metadata if yt-dlp fails
            return {
                "video_id": video_id,
                "url": full_url,
                "title": f"YouTube Video ({video_id})",
                "channel": "YouTube",
                "duration_seconds": 0,
                "duration_str": "Unknown",
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                "description": ""
            }

    @classmethod
    def get_full_formatted_transcript(cls, video_id: str, group_seconds: int = 30) -> str:
        """
        Retrieves transcript and groups lines into time-block chunks (e.g. every 30 seconds)
        to make LLM context window processing concise and readable with timestamp references.
        """
        entries = cls.get_transcript(video_id)
        if not entries:
            return ""
            
        blocks = []
        current_block_start = entries[0]["start"]
        current_block_lines = []
        
        for entry in entries:
            text = entry["text"].replace("\n", " ")
            if not text:
                continue
                
            # Check if we should start a new timestamp chunk block
            if entry["start"] - current_block_start >= group_seconds and current_block_lines:
                ts_str = cls.format_timestamp(current_block_start)
                block_text = f"[{ts_str}] " + " ".join(current_block_lines)
                blocks.append(block_text)
                current_block_start = entry["start"]
                current_block_lines = [text]
            else:
                current_block_lines.append(text)
                
        if current_block_lines:
            ts_str = cls.format_timestamp(current_block_start)
            block_text = f"[{ts_str}] " + " ".join(current_block_lines)
            blocks.append(block_text)
            
        return "\n\n".join(blocks)
