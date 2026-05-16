from langgraph.types import interrupt

from graph_state import GraphState
from nodes.notes_sync import sync_notes, generate_draft_review_prompt


def human_review(state: GraphState) -> dict:
    idx = state["current_chapter_index"]
    total = len(state["chapters"])
    chapter = state["chapters"][idx]
    chapter_title = chapter["title"]
    clean_reqs = state.get("clean_requirements", "")
    ack = state.get("last_acknowledgment", "")

    prompt = generate_draft_review_prompt(
        idx=idx,
        total=total,
        chapter_title=chapter_title,
        draft=state["draft"],
        chapter_notes=chapter.get("chapter_notes", ""),
        acknowledgment=ack,
    )
    response = interrupt(prompt)

    notes = sync_notes(
        current_clean_requirements=clean_reqs,
        user_input=response,
        context="draft_review",
        chapter_title=chapter_title,
        current_chapter_note=chapter.get("chapter_notes", ""),
    )

    # update chapter_notes
    updated_chapters = list(state["chapters"])
    updated_chapters[idx] = {**updated_chapters[idx], "chapter_notes": notes.chapter_note}

    base = {
        "clean_requirements": notes.updated_clean_requirements,
        "chapters": updated_chapters,
        "last_acknowledgment": notes.acknowledgment,
    }

    if notes.intent == "approve":
        return {**base, "action": "approve"}

    if notes.intent == "note_only":
        return {**base, "action": "note_only"}

    if notes.intent == "regenerate":
        return {
            **base,
            "action": "regenerate",
            "raw_feedback": response,
            "text_analysis": [],
            "feedback_notes": [],
        }

    # refine
    return {**base, "action": "refine", "raw_feedback": response}
