from langgraph.types import interrupt

from graph_state import GraphState
from nodes.notes_sync import sync_notes, generate_review_prompt


def review_chapter(state: GraphState) -> dict:
    chapters = state["chapters"]
    clean_reqs = state.get("clean_requirements", "")
    ack = state.get("last_acknowledgment", "")

    prompt = generate_review_prompt(chapters, clean_reqs, ack)
    response = interrupt(prompt)

    notes = sync_notes(
        current_clean_requirements=clean_reqs,
        user_input=response,
        context="chapter_review",
        chapters=chapters,
    )

    # Update chapter_notes if a specific chapter was targeted
    updated_chapters = list(chapters)
    idx = notes.target_chapter_index
    if idx >= 0 and idx < len(updated_chapters) and notes.chapter_note:
        updated_chapters[idx] = {
            **updated_chapters[idx],
            "chapter_notes": notes.chapter_note,
        }

    base = {
        "clean_requirements": notes.updated_clean_requirements,
        "last_acknowledgment": notes.acknowledgment,
        "chapters": updated_chapters,
    }

    if notes.intent == "approve":
        return {**base, "action": "approve"}

    if notes.intent == "note_only":
        return {**base, "action": "note_only"}

    # modify_chapters
    past = state.get("feedback_notes") or []
    return {**base, "action": "refine", "feedback_notes": past + [response]}
