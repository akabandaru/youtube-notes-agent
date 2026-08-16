# 🧠 Walkthrough & Code Guide - YouTube Video Learning & Notes Agent

We have built a YouTube Video Learning & Notes Agent with a Python backend and an interactive web dashboard.

---

## 🛠️ Step-by-Step Implementation & Code Explanation

### Step 1: Project Setup, Dependencies & Git Initialization
- **Location**: `/Users/akankshbandaru/Documents/youtube-notes-agent`
- **Dependencies (`requirements.txt`)**:
  - `fastapi`: High-performance asynchronous Python web backend.
  - `youtube-transcript-api`: Fetches time-coded subtitles/transcripts from YouTube.
  - `yt-dlp`: Metadata extractor (title, thumbnail, channel, duration).
  - `google-genai`: Official Google SDK for Gemini LLMs.
  - `pydantic`: Schema validation and structured JSON data modeling.
- **Git**: Initialized `git` repository with `.gitignore`, `LICENSE` (MIT), and production `README.md`.

---

### Step 2: YouTube Subtitle & Metadata Extractor (`app/youtube_extractor.py`)
**How it works**:
1. `extract_video_id(url)`: Uses regex to extract the 11-character YouTube video ID regardless of URL format (`watch?v=...`, `youtu.be/...`, `shorts/...`).
2. `get_transcript(video_id)`: Tries manually created English subtitles first, falls back to auto-generated English, and if neither exists, fetches and translates foreign subtitles.
3. `get_full_formatted_transcript(...)`: Bundles subtitle fragments into 30-second timestamped blocks (`[01:30] ... text ...`) to provide clear temporal context to the AI model.

---

### Step 3: AI Agent Prompt Engine (`app/note_generator.py`)
**How it works**:
1. Uses **Pydantic Schemas** (`GeneratedStudySheet`, `ChapterBreakdown`, `MentalModelDiagram`, `ActiveRecallQuestion`) to guarantee that Gemini returns valid JSON matching our exact structure.
2. Implements **System Prompt Engineering** enforcing learning science principles:
   - **Feynman Technique**: Simplifies complex topics using real-world analogies.
   - **Mermaid.js Diagrams**: Auto-generates flowcharts/visual diagrams.
   - **Active Recall**: Generates flashcard-style Q&A testing *why* and *how*.
   - **Obsidian / Notion Ready**: Generates a pre-formatted Markdown document complete with metadata tags and collapsible HTML `<details>` tags for answers.

---

### Step 4: FastAPI REST Web Backend (`app/main.py`)
**Endpoints**:
- `POST /api/generate-notes`: Accepts `{ url, custom_focus, api_key }`. Fetches transcripts, invokes Gemini, saves the generated JSON to `output_notes/{video_id}.json` for instant caching.
- `GET /api/history`: Lists previously generated study sheets.
- `GET /api/notes/{video_id}`: Retrieves cached note sheets.
- `GET /`: Serves the single-page learning dashboard UI.

---

### Step 5: Glassmorphism Web Dashboard (`app/templates/index.html`)
- Built with Tailwind CSS, FontAwesome icons, `marked.js` (Markdown renderer), and `Mermaid.js` (diagram renderer).
- Features:
  - Real-time progress bar (Metadata -> Transcripts -> Gemini Processing -> Render).
  - Interactive Tabs: **Feynman Intuition**, **Timestamps & Chapters** (with direct links to video timestamps), **Mental Model Diagrams**, **Active Recall Flashcards**, and **Raw Markdown**.
  - One-click export to **Obsidian (`.md`)** and **Notion**.
  - Slide-over drawer for past note sheet history.

---

## 🧪 Verification Results

### Automated Tests
Run unit test suite:
```bash
source .venv/bin/activate
python -m pytest tests/
```
Output:
`7 passed in 0.25s` (Testing URL extractor, timestamp formatting, Pydantic schemas, and FastAPI endpoints).

### Local Running Status
Launch the FastAPI dev server:
```bash
cd /Users/akankshbandaru/Documents/youtube-notes-agent
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- Open in browser: **`http://localhost:8000`**

---

## 🚀 How to Push This Repository to Your GitHub

To upload this project to your personal GitHub account:

1. Create a new repository on [GitHub](https://github.com/new) named `youtube-notes-agent` (leave it empty without initializing README).
2. Run these commands in your terminal:
```bash
cd /Users/akankshbandaru/Documents/youtube-notes-agent
git remote add origin https://github.com/<your-github-username>/youtube-notes-agent.git
git push -u origin main
```
