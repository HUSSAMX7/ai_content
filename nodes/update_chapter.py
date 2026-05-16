from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm
from schemas import ChapterList

_structured_llm = llm.with_structured_output(ChapterList)


def update_chapter(state: GraphState) -> dict:
    current_chapters = state["chapters"]
    notes = state.get("feedback_notes") or []
    modification_request = notes[-1]

    lines = []
    for i, ch in enumerate(current_chapters):
        line = f"{i+1}. {ch['title']}"
        if ch.get("description"):
            line += f" → {ch['description']}"
        lines.append(line)
    numbered = "\n".join(lines)

    messages = [
        SystemMessage(
            content=(
                "You are a helpful assistant managing a list of chapters.\n"
                "Each chapter has a title and an optional description.\n"
                "Apply the user's modification precisely (add, remove, rename, reorder, update description).\n"
                "Return the full updated list."
            )
        ),
        HumanMessage(
            content=(
                f"Current chapters:\n{numbered}\n\n"
                f"Modification request: {modification_request}"
            )
        ),
    ]

    result: ChapterList = _structured_llm.invoke(messages)
    return {"chapters": [{"title": c.title, "description": c.description, "chapter_notes": c.chapter_notes} for c in result.chapters]}
