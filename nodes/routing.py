from graph_state import GraphState


def _has_references(state: GraphState) -> bool:
    return bool(state.get("sample", "").strip())


def route_entry(state: GraphState) -> str:
    return "analyze_template" if state["mode"] == "template" else "collect_input"


def route_after_collect_input(state: GraphState) -> str:
    return (
        "collect_input"
        if state.get("action") == "continue_interview"
        else "propose_default_chapters"
    )


def route_after_human_review(state: GraphState) -> str:
    action = state["action"]
    if action == "approve":
        return "approve_chapter"
    if action == "regenerate":
        return "generate_chapter"
    if action == "note_only":
        return "human_review"
    return "refine_chapter"


def route_after_approve(state: GraphState) -> str:
    idx = state["current_chapter_index"]  # already incremented by approve_chapter
    if idx >= len(state["chapters"]):
        return "prepare_export"
    if _has_references(state):
        return "extract_chapter_samples"
    return "generate_chapter"


def route_after_chapters_review(state: GraphState) -> str:
    action = state["action"]
    if action == "approve":
        if _has_references(state):
            return "extract_chapter_samples"
        return "generate_chapter"
    if action == "note_only":
        return "review_chapter"
    return "update_chapter"
