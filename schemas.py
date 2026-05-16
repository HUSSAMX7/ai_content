from pydantic import BaseModel, Field
from typing import Literal, Optional

class Chapter(BaseModel):
    title: str
    description: str = ""
    chapter_notes: str = ""


class ChapterList(BaseModel):
    chapters: list[Chapter]


class NotesSync(BaseModel):
    updated_clean_requirements: str = Field(
        ...,
        description=(
            "Updated clean requirements after considering the user's latest input. "
            "If the input contains new requirements, corrections, or removals — apply them. "
            "If the input is just approval or minor feedback, return the current requirements unchanged."
        ),
    )
    chapter_note: str = Field(
        "",
        description=(
            "Updated note about the specific chapter being discussed. "
            "Read the existing note, then add, modify, or remove information based on the user's input. "
            "Return empty string if no chapter-specific feedback was given."
        ),
    )
    target_chapter_index: int = Field(
        -1,
        description=(
            "0-based index of the chapter the user's note/feedback is about. "
            "-1 if no specific chapter was mentioned or the input is general."
        ),
    )
    acknowledgment: str = Field(
        "",
        description=(
            "A brief Arabic sentence confirming what was done with the user's input. "
            "Example: 'تمام، سجلت ملاحظتك على الفصل الثاني' or 'تم تحديث المتطلبات'. "
            "Keep empty if user just approved."
        ),
    )
    intent: str = Field(
        ...,
        description=(
            "Classify the user's intent. Must be one of the valid intents provided in the prompt."
        ),
    )


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