import pytest
from app.youtube_extractor import YouTubeExtractor

def test_extract_video_id_valid_urls():
    """Test extracting video ID from standard YouTube URL variations."""
    valid_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ]
    
    for url, expected_id in valid_cases:
        assert YouTubeExtractor.extract_video_id(url) == expected_id

def test_extract_video_id_invalid_urls():
    """Test that invalid URLs raise ValueError."""
    invalid_cases = [
        "https://google.com",
        "invalid_id_length",
        "",
        "https://youtube.com/watch?v=short"
    ]
    
    for invalid in invalid_cases:
        with pytest.raises(ValueError):
            YouTubeExtractor.extract_video_id(invalid)

def test_format_timestamp():
    """Test seconds formatting into MM:SS and HH:MM:SS."""
    assert YouTubeExtractor.format_timestamp(0) == "00:00"
    assert YouTubeExtractor.format_timestamp(65) == "01:05"
    assert YouTubeExtractor.format_timestamp(3665) == "01:01:05"
