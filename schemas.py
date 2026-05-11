from pydantic import BaseModel, Field
from typing import Literal, Optional

class Chapter(BaseModel):
    title: str
    description: str = ""


class ChapterList(BaseModel):
    chapters: list[Chapter]


class ReviewDecision(BaseModel):
    action: str  # "approve", "refine", or "regenerate"


class InterviewAssimilation(BaseModel):

    updated_memo: str = Field(
        ...,
        description="Full updated requirements memo (Arabic, markdown-style). Merge the new answer; keep prior facts that still hold.",
    )

    clean_requirements: str = Field(
        ...,
        description="Clean requirements memo (Arabic, markdown-style). Remove any extra information that is not related to the requirements. Keep only the requirements.",
    )

    interview_done: bool = Field(
        ...,
        description="True if information is sufficient to draft content, or user explicitly ended (e.g. done, enough, finished).",
    )