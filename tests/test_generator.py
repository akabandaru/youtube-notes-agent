import pytest
from app.note_generator import GeneratedStudySheet, ChapterBreakdown, MentalModelDiagram, VocabularyTerm, ActiveRecallQuestion

def test_generated_study_sheet_schema():
    """Verify that Pydantic study sheet schema instantiates and serializes correctly."""
    sample_sheet = GeneratedStudySheet(
        one_sentence_summary="Neural networks are mathematical function approximators trained via gradient descent.",
        feynman_explanation="Imagine learning to throw a basketball into a hoop in the dark. Every time you miss, someone tells you if you threw too high or too low. You adjust your angle slightly each time until you hit the net.",
        chapters=[
            ChapterBreakdown(
                timestamp="[00:45]",
                title="Introduction to Perceptrons",
                explanation="The basic building block of a neural network that takes inputs, multiplies by weights, and passes through an activation function.",
                key_takeaways=["Weights dictate feature importance", "Bias shifts activation threshold"]
            )
        ],
        mental_models=[
            MentalModelDiagram(
                title="Forward Pass Flow",
                diagram_type="mermaid",
                code="graph LR; A[Inputs] --> B[Weighted Sum]; B --> C[Activation]; C --> D[Output];",
                explanation="Flow of data from input features to final prediction."
            )
        ],
        vocabulary=[
            VocabularyTerm(
                term="Gradient Descent",
                simple_definition="Algorithm to minimize prediction error by moving step-by-step down the error landscape.",
                analogy="Walking down a foggy mountain by always taking a step in the steepest downward direction."
            )
        ],
        active_recall_quiz=[
            ActiveRecallQuestion(
                question="Why is non-linearity required in neural networks?",
                hint="Think about combining multiple linear equations.",
                answer="Without non-linear activation functions, stacking multiple neural network layers just mathematically collapses into a single linear layer.",
                concept_tested="Activation Functions"
            )
        ],
        markdown_export="# Neural Networks 101\n\nSample Markdown Note Sheet."
    )

    assert sample_sheet.one_sentence_summary.startswith("Neural networks")
    assert len(sample_sheet.chapters) == 1
    assert sample_sheet.mental_models[0].diagram_type == "mermaid"
    assert len(sample_sheet.active_recall_quiz) == 1
