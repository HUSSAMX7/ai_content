from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm


def refine_chapter(state: GraphState) -> dict:
    idx = state["current_chapter_index"]
    chapter = state["chapters"][idx]
    chapter_title = chapter["title"]
    chapter_description = chapter.get("description", "")
    chapter_notes = chapter.get("chapter_notes", "")
    sample = state["sample"]
    clean_requirements = state.get("clean_requirements", "")
    text_analysis = state.get("text_analysis", [])
    feedback_notes = state.get("feedback_notes", [])

    history_block = ""
    if text_analysis:
        history_block = "Revision history:\n"
        for i, (ta, fn) in enumerate(zip(text_analysis, feedback_notes)):
            history_block += (
                f"\nRound {i+1}:\n"
                f"  TEXT_ANALYSIS{i+1}: {ta}\n"
                f"  FEEDBACK_NOTES{i+1}: {fn}\n"
            )
        history_block += "\n"

    system_prompt = (
        "You are a specialist technical writer. Revise one chapter based on a structured revision history.\n\n"
        "Strict rules:\n"
        "1) Apply the LATEST feedback_notes precisely.\n"
        "2) Do NOT undo any fix from previous rounds.\n"
        "3) Keep output scoped to this chapter only.\n"
        "4) Keep the same language as the references.\n"
        "5) Preserve coherence and technical depth.\n\n"
        f"References (style and structure only):\n{sample}"
    )

    # Build user requirements block
    reqs_block = ""
    if clean_requirements:
        reqs_block += f"\n== USER REQUIREMENTS (MUST FOLLOW) ==\n{clean_requirements}\n== END REQUIREMENTS ==\n"
    if chapter_notes:
        reqs_block += f"\n== CHAPTER-SPECIFIC NOTES FROM USER ==\n{chapter_notes}\n== END NOTES ==\n"

    user_prompt = f"Chapter title: {chapter_title}\n"
    if chapter_description:
        user_prompt += f"Chapter description: {chapter_description}\n"
    user_prompt += reqs_block
    user_prompt += (
        f"\n{history_block}"
        f"Current draft:\n{state['draft']}\n\n"
        "Revise the chapter according to the latest feedback_notes "
        "while preserving all previous corrections. "
        "You MUST also follow the user requirements and chapter notes above."
    )

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    response = llm.invoke(messages)
    return {"draft": response.content}