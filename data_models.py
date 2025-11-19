# src/data_models.py
from pydantic import BaseModel, Field
from typing import List

# Model for the detailed feedback on a single component
class FeedbackComponent(BaseModel):
    area: str = Field(description="The area analyzed (e.g., 'Visuals', 'Audio', 'Pacing').")
    problem: str = Field(description="A clear, identified problem in this area (e.g., 'Harsh backlighting').")
    solution: str = Field(description="A specific, actionable solution for the creator (e.g., 'Use a ring light in front').")

# The main output model for the primary analysis
class VideoAnalysisResult(BaseModel):
    overall_score: int = Field(..., ge=1, le=10, description="Overall quality score from 1 (poor) to 10 (pro-level).")
    review_check: bool = Field(description="True if the score is low (e.g., <5) and needs human review, otherwise False.")
    summary_insight: str = Field(description="A single sentence summary of the video's biggest strength and weakness.")
    detailed_feedback: List[FeedbackComponent]