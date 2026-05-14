from langgraph.types import interrupt

from graph_state import GraphState
from nodes.absorb_context import absorb_context
from nodes.classify_response import _classify_response


def human_review(state: GraphState) -> dict:
    idx = state["current_chapter_index"]
    total = len(state["chapters"])
    chapter_title = state["chapters"][idx]["title"]

    response = interrupt(
        f"الفصل {idx + 1} من {total}: {chapter_title}\n\n"
        f"{state['draft']}\n\n"
        "────────\n"
        "راجع المسودة. إذا مناسبة لك، اكتب لي موافق وننتقل للفصل التالي.\n"
        "وإذا تحتاج تعديل، اكتب ملاحظاتك بشكل واضح عشان نحدّث النص.\n"
        "💡 تقدر أيضاً تضيف معلومات جديدة وبتنحفظ تلقائياً."
    )

    # ── امتصاص أي معلومة جديدة من الرد ──
    context_updates = absorb_context(response, state)

    action = _classify_response(response)
    if action == "approve":
        return {"action": "approve", **context_updates}
    if action == "regenerate":
        return {
            "action": "regenerate",
            "raw_feedback": response,
            "text_analysis": [],
            "feedback_notes": [],
            **context_updates,
        }
    return {"action": "refine", "raw_feedback": response, **context_updates}
