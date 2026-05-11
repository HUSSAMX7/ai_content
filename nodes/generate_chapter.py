from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm


def generate_chapter(state: GraphState) -> dict:
    idx = state["current_chapter_index"]
    chapter = state["chapters"][idx]
    chapter_title = chapter["title"]
    chapter_description = chapter.get("description", "")
    chapter_samples = state["chapter_samples"]
    resource = state["resource"]
    regeneration_notes = state.get("regeneration_notes") or []
    raw_feedback = state.get("raw_feedback", "")

    # debug print
    print("\n" + "=" * 80)
    print(f"[DEBUG] chapter_samples for chapter: {chapter_title}")
    print(chapter_samples)
    print("=" * 80 + "\n")
    # end debug print

    # Combine all prior rejection notes plus current feedback into a full avoidance list
    all_rejection_notes = list(regeneration_notes)
    if raw_feedback:
        all_rejection_notes.append(raw_feedback)

    avoidance_block = ""
    if all_rejection_notes:
        avoidance_block = (
            "\n\nPREVIOUS ATTEMPTS WERE REJECTED — DO NOT repeat these approaches:\n"
            + "\n".join(f"- {note}" for note in all_rejection_notes)
            + "\nYou MUST produce a distinctly different version in structure, angle, and phrasing.\n"
        )

    system_prompt = (
        "You are a specialist technical writer. Write one chapter by learning "
        "style and structure from the provided references.\n\n"
        "Strict rules:\n"
        "1) Write only the requested chapter. Do not include other chapters.\n"
        "2) The extracted chapter samples are style/structure guides. Do not copy their project-specific content.\n"
        "3) Keep the output scoped to this chapter only, in the same language as the references.\n"
        "4) If multiple samples are provided, synthesize them into one coherent chapter.\n"
        "5) Resolve conflicts by preferring the most context-relevant and repeated points.\n"
        "6) Do not produce a shallow summary; maintain comparable depth to the reference chapter type.\n"
        "7) Infer structure dynamically from relevant references: if references show multiple themes, "
        "organize the chapter into clear numbered sub-sections; if not, keep it simpler.\n"
        "8) Each sub-section should contain concrete, operational detail (processes, criteria, or examples), "
        "not generic statements.\n"
        "9) Use content from at least two chapter samples when possible, especially for overlapping themes.\n"
        "10) Never mention the source file names, tags, or reference project identity in the final text.\n"
        "11) Samples may come from multiple source files. Always merge patterns across samples; do not rely on a single sample."
        f"{avoidance_block}\n\n"
        f"Chapter-matched samples:\n{chapter_samples}\n\n"
        f"General project context:\n{resource}"
    )

    user_prompt = (
        f"Chapter title: {chapter_title}\n"
        f"General project context:\n{resource}"
    )
    if chapter_description:
        user_prompt += f"Chapter description: {chapter_description}\n"
    user_prompt += (
        f"\nTask:\n"
        f"- Produce only the '{chapter_title}' chapter.\n"
        "- First infer a suitable internal outline from the chapter-matched samples, then write the final chapter.\n"
        "- Keep depth comparable to the corresponding reference chapter type.\n"
        "- Prefer synthesis over paraphrased summary.\n"
        "- Do not output planning notes or outline drafts; output final chapter text only."
    )

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    response = llm.invoke(messages)
    # draft = f"# {chapter_title}\n\n{response.content}"

    return {
        "draft": response.content,
        "text_analysis": [],
        "feedback_notes": [],
        "raw_feedback": "",
        "regeneration_notes": all_rejection_notes,
    }
