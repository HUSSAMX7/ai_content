from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm
from schemas import ChapterList

_structured_llm = llm.with_structured_output(ChapterList)


def propose_default_chapters(state: GraphState) -> dict:
    clean_requirements = (state.get("clean_requirements") or "").strip()

    messages = [
        SystemMessage(
            content=(
                "You are a senior technical documentation architect specializing in Arabic government and enterprise deliverables.\n\n"
                "Your task: Propose a coherent, professional structure based on a deep analysis of the requirements below.\n\n"
                "## Step 1 — Analyze the requirements\n"
                "Before proposing anything, reason internally about:\n"
                "- What is the output format? Infer whether this is a technical report, PowerPoint presentation, administrative memo, or other — based solely on the requirements\n"
                "- Who is the target audience? (technical team, executive, administrative body?)\n"
                "- What domain/topic is involved? (NLP, digital transformation, legal, etc.)\n"
                "- What is the document's purpose? (informing, seeking approval, project handover, etc.)\n\n"
                "## Step 2 — Fill logical gaps\n"
                "The user's requirements may be incomplete. Use your domain knowledge to:\n"
                "- Infer missing but necessary sections that any professional output of this type MUST include\n"
                "- Add sections that serve the stated audience and purpose, even if not explicitly requested\n"
                "- Ensure the structure flows logically (e.g., context → problem → solution → results → recommendations)\n\n"
                "## Step 3 — Determine section count\n"
                "If the user specified a count, use it exactly.\n"
                "If not, determine the appropriate count based on document type, topic depth, and audience formality.\n\n"
                "## Output rules\n"
                "- Write all titles and descriptions in Arabic\n"
                "- Titles must be specific, non-redundant, and ordered logically\n"
                "- Each description should clarify what the section covers\n"
                "- Do NOT ask questions. Do NOT add commentary outside the structured output."
            )
        ),
        HumanMessage(content=f"Clean requirements:\n{clean_requirements}"),
    ]
    result = _structured_llm.invoke(messages)
    chapters = [{"title": c.title, "description": c.description} for c in result.chapters]
    return {"chapters": chapters}