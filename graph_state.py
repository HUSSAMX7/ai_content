from typing import Annotated, TypedDict
import operator


class GraphState(TypedDict):
    sample: str
    chapter_samples: str
    template: str
    resource: str
    mode: str
    chapters: list[dict]
    current_chapter_index: int
    draft: str
    raw_feedback: str
    text_analysis: list[str]
    feedback_notes: list[str]
    action: str
    regeneration_notes: list[str]
    generated_chapters: Annotated[list[str], operator.add]
    requirements_memo: str
    clean_requirements: str
    interview_logs: list[dict]
    final_content: str