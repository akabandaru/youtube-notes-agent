# 🧠 YouTube Learning & Notes Agent

> An AI agent that turns YouTube videos into detailed, high-retention study guides using the Feynman Technique, Active Recall, and Mental Model visual diagrams.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Why This Agent?

Watching educational videos on YouTube (computer science, AI, physics, system design, how things work) is great, but passive watching leads to fast knowledge decay. 

This agent uses **cognitive science & active learning principles**:
- **Feynman Technique**: Simplifies complex ideas into jargon-free intuition ("Explain like I'm 5").
- **Timestamped Deep Dives**: Links key concepts directly back to exact video moments (`[03:45]`).
- **Mental Models & Diagrams**: Auto-generates `Mermaid.js` flowcharts and ASCII diagrams for visual learners.
- **Active Recall Flashcards**: Includes interactive self-testing questions to lock knowledge into long-term memory.
- **Obsidian & Notion Ready**: Export formatted Markdown directly to your personal knowledge base.

---

## 🏗️ Architecture Overview

```
 ┌────────────────────────────────────────────────────────┐
 │                   Frontend Web UI                      │
 │   - URL Input & Custom Focus Areas                     │
 │   - Interactive Flashcards, Diagrams & Math (KaTeX)    │
 │   - 1-Click Obsidian (.md) & Notion Exporter           │
 └───────────────────────────┬────────────────────────────┘
                             │ REST API
 ┌───────────────────────────▼────────────────────────────┐
 │               FastAPI Backend (Python)                 │
 │   - youtube_extractor.py (Subtitles, metadata, yt-dlp)│
 │   - note_generator.py (Gemini LLM Prompt Engine)       │
 └───────────────────────────┬────────────────────────────┘
                             │ Google GenAI SDK
 ┌───────────────────────────▼────────────────────────────┐
 │               Google Gemini AI Engine                  │
 └────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- A Google Gemini API Key (Get one for free at [Google AI Studio](https://aistudio.google.com/app/api-keys))

### 2. Installation

Clone the repository and enter the directory:
```bash
git clone https://github.com/<your-username>/youtube-notes-agent.git
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

### 3. Environment Setup

Create a `.env` file from the template:
```bash
cp .env.example .env
```
Edit `.env` and add your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 4. Run the Agent

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
Open your browser and navigate to: **`http://localhost:8000`**

---

## 📁 Repository Structure

```
youtube-notes-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI endpoints & static routing
│   ├── youtube_extractor.py   # Transcript fetching & timestamp parsing
│   ├── note_generator.py      # LLM structured prompt & note generation
│   └── templates/
│       └── index.html         # Single-page interactive dashboard
├── tests/
│   └── test_extractor.py      # Unit tests for URL parser & transcript logic
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md                  # Project documentation
```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
