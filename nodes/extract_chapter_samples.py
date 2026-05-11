from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm


def extract_chapter_samples(state: GraphState) -> dict:
    idx = state["current_chapter_index"]
    chapter = state["chapters"][idx]
    chapter_title = chapter["title"]
    chapter_description = chapter.get("description", "")
    sample = state["sample"]
    if not sample.strip():
        return {"chapter_samples": ""}

    system_prompt = (
        "You extract only the relevant chapter text from multi-sample references.\n\n"
        "Rules:\n"
        "1) The input contains multiple source files wrapped like [SOURCE: ...] ... [END SOURCE: ...].\n"
        "2) For EACH source, extract ONLY the section that matches the requested chapter title.\n"
        "3) If exact title is not found, pick the closest semantic match.\n"
        "3) Matching is semantic, not literal: accept small wording differences, rephrasing, synonyms, "
        "or heading variants that mean the same chapter.\n"
        "4) Do not include unrelated chapters.\n"
        "5) Preserve the original language.\n"
        "6) Output format strictly:\n"
        "   [CHAPTER SAMPLE: <source_name>]\n"
        "   <extracted text>\n"
        "   [END CHAPTER SAMPLE]\n"
        "7) If a source has no match, output:\n"
        "   [CHAPTER SAMPLE: <source_name>]\n"
        "   NOT_FOUND\n"
        "   [END CHAPTER SAMPLE]\n"
        "8) Do not add explanations."
    )

    user_prompt = (
        f"Target chapter title: {chapter_title}\n"
        f"Target chapter description: {chapter_description}\n\n"
        f"References:\n{sample}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)

    # this is what generate_chapter should consume
    return {"chapter_samples": response.content}