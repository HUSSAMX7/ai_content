from graph_state import GraphState


def _has_references(state: GraphState) -> bool:
    return bool(state.get("sample", "").strip())


def route_entry(state: GraphState) -> str:
    return "analyze_template" if state["mode"] == "template" else "collect_input"


def route_after_human_review(state: GraphState) -> str:
    action = state["action"]
    if action == "approve":
        return "approve_chapter"
    if action == "regenerate":
        return "generate_chapter"
    return "refine_chapter"


def route_after_approve(state: GraphState) -> str:
    idx = state["current_chapter_index"]  # already incremented by approve_chapter
    if idx >= len(state["chapters"]):
        return "prepare_export"
    if _has_references(state):
        return "extract_chapter_samples"
    return "generate_chapter"


def route_after_chapters_review(state: GraphState) -> str:
    if state["action"] != "approve":
        return "update_chapter"
    if _has_references(state):
        return "extract_chapter_samples"
    return "generate_chapter"
