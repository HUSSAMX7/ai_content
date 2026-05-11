from langgraph.types import interrupt

from graph_state import GraphState
from nodes.classify_response import _classify_response


def review_chapter(state: GraphState) -> dict:
    chapters = state["chapters"]

    lines = []
    for i, ch in enumerate(chapters):
        line = f"{i+1}. {ch['title']}"
        if ch.get("description"):
            line += f"\n   → {ch['description']}"
        lines.append(line)
    numbered = "\n".join(lines)


    response = interrupt(
    f"هذي الفصول اللي اقترحتها لك:\n\n{numbered}\n\n"
    "اكتب لي موافق عشان نبدأ التوليد، "
    "أو اكتب التعديل اللي تبيه (مثلاً: احذف الفصل الثاني، أضف فصل عن كذا):"
    )

    action = _classify_response(response)
    if action == "approve":
        return {"action": "approve"}
    past = state.get("feedback_notes") or []
    return {"action": "refine", "feedback_notes": past + [response]}
