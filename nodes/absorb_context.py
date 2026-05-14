"""
طبقة امتصاص السياق — تستخرج أي معلومة جديدة من رد المستخدم
وتحفظها في المكان الصحيح في الـ state.

تُستدعى من أي نود فيه تفاعل بشري (review_chapter, human_review)
قبل تصنيف الرد.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm_fast
from schemas import ContextAbsorption


ABSORB_PROMPT = """\
You are an information extraction specialist.

You receive a user's response during a document review session.
Your job is to detect whether the response contains NEW information, context,
or instructions — beyond just saying "approve", "reject", or requesting
structural changes (add/remove/reorder chapters).

## What counts as new info:
- Project facts: budget, timeline, team, domain details, technologies
- Chapter-specific notes: "chapter 3 should focus on security"
- General writing instructions: "use formal Arabic", "target executives"
- Corrections to previously stated info: "actually the budget is 3M not 2M"

## What does NOT count:
- Pure approval: "ok", "good", "approved", "موافق"
- Pure rejection: "rewrite", "أعد الكتابة"
- Structural changes: "remove chapter 2", "add a chapter about X"
  (these are handled by other nodes — but if combined with info, extract the info part)

Analyze carefully. A response can contain BOTH a structural request AND new info.
Extract only the informational part."""

_absorb_llm = llm_fast.with_structured_output(ContextAbsorption)


def absorb_context(user_response: str, state: GraphState) -> dict:
    """
    Extracts new information from a user response and returns state updates.
    
    Call this BEFORE classifying the response as approve/refine/regenerate.
    Merge the returned dict into the node's return value.
    """
    chapters = state.get("chapters") or []
    clean_reqs = state.get("clean_requirements") or ""

    chapter_list = "\n".join(
        f"{i+1}. {ch['title']}" for i, ch in enumerate(chapters)
    )

    result: ContextAbsorption = _absorb_llm.invoke([
        SystemMessage(content=ABSORB_PROMPT),
        HumanMessage(
            content=(
                f"Current chapters:\n{chapter_list}\n\n"
                f"Current requirements:\n{clean_reqs}\n\n"
                f"User response:\n{user_response}"
            )
        ),
    ])

    if not result.has_new_info:
        return {}

    updates: dict = {}

    # ── 1. معلومات مشروع جديدة → تُضاف للمتطلبات ──
    if result.new_project_info.strip():
        separator = "\n" if clean_reqs.strip() else ""
        updates["clean_requirements"] = (
            clean_reqs + separator + result.new_project_info
        )

    # ── 2. ملاحظات على فصول محددة → تُضاف لوصف الفصل ──
    if result.chapter_notes:
        updated_chapters = [dict(ch) for ch in chapters]  # shallow copy
        for note in result.chapter_notes:
            idx = note.chapter_index - 1  # convert to 0-based
            if 0 <= idx < len(updated_chapters):
                ch = updated_chapters[idx]
                existing_desc = ch.get("description", "")
                ch["description"] = (
                    f"{existing_desc}\n[ملاحظة]: {note.note}".strip()
                )
        updates["chapters"] = updated_chapters

    # ── 3. تعليمات كتابة عامة → تُضاف للملاحظات العامة ──
    if result.general_writing_notes:
        existing_notes = list(state.get("global_notes") or [])
        updates["global_notes"] = existing_notes + result.general_writing_notes

    return updates
