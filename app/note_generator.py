import os
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Pydantic Schemas for Structured Learning Output
# ---------------------------------------------------------------------------

class ChapterBreakdown(BaseModel):
    timestamp: str = Field(description="Formatted timestamp link e.g. [03:15]")
    title: str = Field(description="Descriptive chapter/topic section title")
    explanation: str = Field(description="Detailed yet logically concise explanation of the topic discussed")
    key_takeaways: List[str] = Field(description="Bullet points of essential rules, mechanisms, or insights")

class MentalModelDiagram(BaseModel):
    title: str = Field(description="Name of the mental model, system component, or process visual")
    diagram_type: str = Field(description="'mermaid' or 'ascii'")
    code: str = Field(description="Mermaid.js diagram code or clean ASCII art diagram")
    explanation: str = Field(description="Brief explanation of how to interpret this visual model")

class VocabularyTerm(BaseModel):
    term: str = Field(description="Key concept, acronym, or technical term")
    simple_definition: str = Field(description="Clear definition in simple language")
    analogy: str = Field(description="Real-world intuitive analogy (e.g. 'Like a traffic cop directing cars')")

class ActiveRecallQuestion(BaseModel):
    question: str = Field(description="A thought-provoking self-test question to test retention")
    hint: str = Field(description="A subtle hint to aid memory recall")
    answer: str = Field(description="Comprehensive answer explaining the underlying 'why' and 'how'")
    concept_tested: str = Field(description="The specific mental model or sub-topic tested")

class GeneratedStudySheet(BaseModel):
    one_sentence_summary: str = Field(description="The core thesis / TL;DR of the video in one sentence")
    feynman_explanation: str = Field(description="Explain like I'm 5 (ELI5) summary using intuitive analogies and no jargon")
    chapters: List[ChapterBreakdown] = Field(description="Detailed topic breakdown ordered chronologically by video timestamps")
    mental_models: List[MentalModelDiagram] = Field(description="1-2 Mermaid flowcharts or system visual diagrams")
    vocabulary: List[VocabularyTerm] = Field(description="Key terms cheat sheet")
    active_recall_quiz: List[ActiveRecallQuestion] = Field(description="5-8 active recall flashcards/questions for long-term retention")
    markdown_export: str = Field(description="Full, beautifully formatted Markdown note sheet ready for Obsidian/Notion export")


# ---------------------------------------------------------------------------
# Note Generator Agent Engine
# ---------------------------------------------------------------------------

class NoteGeneratorAgent:
    """
    AI Agent that communicates with Google Gemini API to synthesize video transcripts
    into structured Feynman learning sheets and active recall quizzes.
    """
    
    SYSTEM_INSTRUCTION = """
You are a World-Class Educator and Cognitive Specialist. Your goal is to convert YouTube video transcripts into a high-retention, logically concise, and detailed Study & Learning Sheet.

You follow strict principles of learning science:
1. **Feynman Technique**: Explain complex concepts using intuitive, simple analogies before diving into technical details. Avoid fluff, filler words, or generic intros.
2. **Structural Clarity**: Break content down chronologically with exact timestamp references (e.g. [04:20]) so the learner can rewatch specific sections if needed.
3. **Visual Mental Models**: Provide clean, valid Mermaid.js diagrams (`graph TD` or `graph LR` or `sequenceDiagram`) visualizing system flows, architecture, or causal relationships.
4. **Active Recall & Spaced Repetition**: Create high-yield self-quiz questions designed to test deep understanding ("Why does X cause Y?") rather than simple recall ("What is X?").

Always make sure the output markdown is clean, elegant, and ready for Obsidian, Notion, or personal note systems.
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes Google GenAI client.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_notes(self, 
                       video_title: str, 
                       channel: str, 
                       transcript_text: str, 
                       custom_focus: Optional[str] = None) -> GeneratedStudySheet:
        """
        Generates structured study sheet using Gemini 2.5 Flash.
        """
        if not self.client:
            raise RuntimeError(
                "Gemini API Key is missing. Please set the GEMINI_API_KEY environment variable or provide an API key."
            )

        prompt = f"""
Analyze the following YouTube video transcript and create a high-retention Study & Learning Sheet.

### VIDEO METADATA
- Title: {video_title}
- Channel/Author: {channel}
{f"- User Specific Focus Area: {custom_focus}" if custom_focus else ""}

### TIME-CODED TRANSCRIPT
{transcript_text}

---
REQUIREMENTS FOR THE STUDY SHEET:
1. **one_sentence_summary**: Single sentence core thesis.
2. **feynman_explanation**: Explain the main topic in 2-3 paragraphs as if explaining to a curious 12-year-old using memorable analogies.
3. **chapters**: Break down the video by major timestamp topics. Include exact timestamp tags like `[02:15]`, clear explanation, and key takeaways.
4. **mental_models**: Provide at least 1 valid Mermaid.js flowchart (`graph TD` or `graph LR`) visualizing the core architecture, data flow, or logical process described in the video.
5. **vocabulary**: Extract 4-8 key technical terms, acronyms, or concepts with simple definitions and real-world analogies.
6. **active_recall_quiz**: 5-8 flashcard-style Q&A questions testing understanding of 'why' and 'how'.
7. **markdown_export**: Combine all the above into a beautiful, production-grade Markdown document formatted for Obsidian (with frontmatter metadata tags, headers, Mermaid block code, and collapsible quiz answers using `<details><summary>Hint & Answer</summary>...</details>`).
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=GeneratedStudySheet,
                    temperature=0.3
                )
            )

            # Parse JSON into Pydantic model
            json_data = json.loads(response.text)
            return GeneratedStudySheet(**json_data)

        except Exception as e:
            raise RuntimeError(f"Error generating notes with Gemini AI: {str(e)}")
