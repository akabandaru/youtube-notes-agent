import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

from app.youtube_extractor import YouTubeExtractor
from app.note_generator import NoteGeneratorAgent, GeneratedStudySheet

# Load environment variables from .env
load_dotenv()

app = FastAPI(
    title="YouTube Learning & Notes Agent API",
    description="Python backend agent transforming YouTube videos into Feynman technique notes and active recall flashcards.",
    version="1.0.0"
)

# Output directory to store generated note sheets for history & caching
NOTES_DIR = Path("output_notes")
NOTES_DIR.mkdir(exist_ok=True)

# Export directory for user's markdown files (e.g. Obsidian vault or ~/Documents/learning_notes)
EXPORT_DIR_SETTING = os.environ.get("NOTES_EXPORT_DIR", str(Path.home() / "Documents" / "learning_notes"))
EXPORT_DIR = Path(EXPORT_DIR_SETTING)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Templates setup
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ---------------------------------------------------------------------------
# Request & Response Data Models
# ---------------------------------------------------------------------------

class GenerateNotesRequest(BaseModel):
    url: str
    custom_focus: Optional[str] = None
    api_key: Optional[str] = None

class VideoNoteResponse(BaseModel):
    video_id: str
    url: str
    title: str
    channel: str
    duration_str: str
    thumbnail_url: str
    generated_at: str
    study_sheet: GeneratedStudySheet

class HistoryItem(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail_url: str
    one_sentence_summary: str
    generated_at: str


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    has_api_key = bool(os.environ.get("GEMINI_API_KEY"))
    return {
        "status": "online",
        "gemini_api_key_configured": has_api_key,
        "notes_saved_count": len(list(NOTES_DIR.glob("*.json")))
    }

@app.post("/api/generate-notes", response_model=VideoNoteResponse)
async def generate_notes(payload: GenerateNotesRequest):
    """
    Extracts transcript from a YouTube URL and generates structured Feynman study notes using Gemini AI.
    """
    # 1. Parse Video ID
    try:
        video_id = YouTubeExtractor.extract_video_id(payload.url)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    # 2. Check cache first
    cached_file = NOTES_DIR / f"{video_id}.json"
    if cached_file.exists() and not payload.custom_focus:
        try:
            with open(cached_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                return VideoNoteResponse(**cached_data)
        except Exception:
            pass  # Re-generate if cache corrupt

    # 3. Extract Metadata & Transcript
    try:
        metadata = YouTubeExtractor.get_metadata(payload.url)
        formatted_transcript = YouTubeExtractor.get_full_formatted_transcript(video_id)
        
        if not formatted_transcript:
            raise HTTPException(status_code=400, detail="Transcript is empty or could not be processed.")
            
    except RuntimeError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error extracting video data: {str(err)}")

    # 4. Initialize AI Agent & Generate Notes
    api_key = payload.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Gemini API Key is missing. Please provide an API key in the UI or set GEMINI_API_KEY in your server .env file."
        )

    agent = NoteGeneratorAgent(api_key=api_key)
    
    try:
        study_sheet = agent.generate_notes(
            video_title=metadata["title"],
            channel=metadata["channel"],
            transcript_text=formatted_transcript,
            custom_focus=payload.custom_focus
        )
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

    # 5. Assemble Response & Persist
    response_data = {
        "video_id": video_id,
        "url": metadata["url"],
        "title": metadata["title"],
        "channel": metadata["channel"],
        "duration_str": metadata["duration_str"],
        "thumbnail_url": metadata["thumbnail_url"],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "study_sheet": study_sheet.model_dump()
    }

    # Save JSON cache to disk
    try:
        with open(cached_file, "w", encoding="utf-8") as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
    except Exception as err:
        print(f"Warning: Could not save note to disk cache: {err}")

    # Auto-export Markdown note to user's learning_notes directory
    try:
        safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in metadata["title"]).strip().replace(" ", "_").lower()
        md_file = EXPORT_DIR / f"{safe_title or video_id}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(study_sheet.markdown_export)
        print(f"Exported note to: {md_file}")
    except Exception as err:
        print(f"Warning: Could not export markdown note: {err}")

    return VideoNoteResponse(**response_data)


@app.get("/api/history", response_model=List[HistoryItem])
def get_history():
    """
    Returns list of previously generated study sheets.
    """
    history = []
    for file_path in sorted(NOTES_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                history.append(HistoryItem(
                    video_id=data["video_id"],
                    title=data["title"],
                    channel=data["channel"],
                    thumbnail_url=data["thumbnail_url"],
                    one_sentence_summary=data["study_sheet"]["one_sentence_summary"],
                    generated_at=data.get("generated_at", "Recently")
                ))
        except Exception:
            continue
    return history


@app.get("/api/notes/{video_id}", response_model=VideoNoteResponse)
def get_note_by_id(video_id: str):
    """
    Retrieves a cached note by YouTube video ID.
    """
    cached_file = NOTES_DIR / f"{video_id}.json"
    if not cached_file.exists():
        raise HTTPException(status_code=404, detail="Note not found.")
        
    try:
        with open(cached_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return VideoNoteResponse(**data)
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error reading note: {str(err)}")


@app.get("/", response_class=HTMLResponse)
def serve_dashboard(request: Request):
    """
    Serves the single-page interactive learning web dashboard.
    """
    return templates.TemplateResponse(request=request, name="index.html")
