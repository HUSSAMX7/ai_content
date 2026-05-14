from pydantic import BaseModel, Field
from typing import Literal, Optional

class Chapter(BaseModel):
    title: str
    description: str = ""


class ChapterList(BaseModel):
    chapters: list[Chapter]


class ReviewDecision(BaseModel):
    action: Literal["approve", "refine", "regenerate"]


class ChapterNote(BaseModel):
    chapter_index: int = Field(
        ...,
        description="1-based index of the target chapter from the provided list.",
    )
    note: str = Field(
        ...,
        description="The instruction, context, or note the user wants applied to this chapter.",
    )


class ContextAbsorption(BaseModel):
    has_new_info: bool = Field(
        ...,
        description=(
            "True if the user's response contains ANY new factual information, "
            "context, instructions, or notes — beyond just approving, rejecting, "
            "or requesting structural changes (add/remove/reorder chapters)."
        ),
    )
    new_project_info: str = Field(
        default="",
        description=(
            "New factual information about the project extracted from the response "
            "(e.g. budget, timeline, team size, domain details, constraints). "
            "Write in Arabic. Leave empty if none."
        ),
    )
    chapter_notes: list[ChapterNote] = Field(
        default_factory=list,
        description=(
            "Notes or instructions targeting SPECIFIC chapters. "
            "Only populate if the user explicitly references a chapter by name or number."
        ),
    )
    general_writing_notes: list[str] = Field(
        default_factory=list,
        description=(
            "General instructions that apply to ALL chapters "
            "(e.g. tone, formality, language, focus area, audience). "
            "Write in Arabic."
        ),
    )


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