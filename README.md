# YouTube Notes Agent

YouTube Notes Agent is a Python application that ingests YouTube video transcripts and synthesizes them into structured, high-retention study sheets. It combines the Feynman Technique, timestamped section breakdowns, visual diagrams, and active recall flashcards into clean Markdown formatted for personal knowledge bases like Obsidian and Notion.

---

## Overview

Passive video consumption often leads to rapid knowledge decay. This tool automates the process of converting dense video content into structured notes designed for long-term retention:

* **Feynman Intuition**: Core concepts explained in simple language using real-world analogies.
* **Timestamp Anchors**: Every chapter breakdown links directly to exact video timestamps (`[03:45]`).
* **Visual Mental Models**: Auto-generated `Mermaid.js` flowcharts for architecture, data flow, and conceptual relationships.
* **Active Recall Flashcards**: Self-testing questions with collapsible hints and full answer explanations.
* **Automated Vault Export**: Generated study sheets are saved directly as `.md` files to `~/Documents/learning_notes`.

---

## System Architecture

```
 ┌────────────────────────────────────────────────────────┐
 │                      Web Dashboard                     │
 │          (HTML5 / Tailwind CSS / JavaScript)           │
 └───────────────────────────┬────────────────────────────┘
                             │ REST API
 ┌───────────────────────────▼────────────────────────────┐
 │                  FastAPI Service Layer                 │
 └─────────────┬────────────────────────────┬─────────────┘
               │                            │
 ┌─────────────▼─────────────┐┌─────────────▼─────────────┐
 │ YouTube Extractor         ││ Note Synthesizer Agent   │
 │ - Subtitles & Timestamps  ││ - Gemini 2.5 Flash       │
 │ - Metadata (yt-dlp)       ││ - Pydantic Schema Guard  │
 └───────────────────────────┘└─────────────┬─────────────┘
                                            │
                               ┌────────────▼────────────┐
                               │ Vault Export (.md)      │
                               │ ~/Documents/learning_notes
                               └─────────────────────────┘
```

---

## Quickstart

### 1. Prerequisites
* Python 3.10+
* Google Gemini API Key ([Get one at Google AI Studio](https://aistudio.google.com/app/api-keys))

### 2. Installation

Clone the repository and enter the directory:
```bash
git clone https://github.com/akabandaru/youtube-notes-agent.git
cd youtube-notes-agent
```

Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` to configure your API key and export directory:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
NOTES_EXPORT_DIR=/Users/akankshbandaru/Documents/learning_notes
```

### 4. Run the Application

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

Open your browser and navigate to:
```
http://localhost:8000
```

---

## Configuration Options

Environment variables can be set in your `.env` file or exported in your shell:

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key used for synthesis. |
| `NOTES_EXPORT_DIR` | No | `~/Documents/learning_notes` | Path where generated `.md` files are auto-saved. |
| `PORT` | No | `8000` | Port for the FastAPI web server. |

---

## Directory Structure

```
youtube-notes-agent/
├── app/
│   ├── main.py                # FastAPI endpoints, routing, and file export
│   ├── note_generator.py      # Gemini agent logic and Pydantic validation schemas
│   ├── youtube_extractor.py   # Subtitle chunking and yt-dlp metadata parser
│   └── templates/
│       └── index.html         # Web dashboard UI
├── output_notes/              # Cached JSON responses
├── tests/                     # Test suite (pytest)
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── WALKTHROUGH.md             # Architecture & developer guide
```

---

## Running Tests

Execute the unit test suite using `pytest`:
```bash
python -m pytest tests/
```

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
