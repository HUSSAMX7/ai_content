from langchain_core.messages import HumanMessage, SystemMessage

from llm_config import llm_fast
from schemas import NotesSync

_structured_llm = llm_fast.with_structured_output(NotesSync)

NOTES_SYNC_PROMPT = """\
You are a requirements and notes tracker for a document generation project.

You receive:
- The current clean requirements
- The user's latest input
- The context (where we are in the workflow)
- Valid intents for this context
- Optionally: chapter list with indices, or a single chapter title and its existing note

Your job:

1. **updated_clean_requirements**: 
   - If the user's input contains new factual requirements, corrections, additions, or removals → update accordingly.
   - If the input is just approval, minor edit instructions, or unrelated → return current requirements UNCHANGED.
   - Never add speculative info. Only confirmed facts from the user.

2. **chapter_note**:
   - If the user gave feedback relevant to a specific chapter → write a concise note summarizing their feedback.
   - If a chapter already has an existing note, READ it first and UPDATE it (merge old + new).
   - If no relevant chapter feedback → return empty string.

3. **target_chapter_index**:
   - If the user mentioned a specific chapter (by number or name), return its 0-based index.
   - If no specific chapter mentioned, return -1.

4. **acknowledgment**:
   - Write a brief Arabic sentence confirming what you did with the user's input.
   - Examples: "تمام، سجلت ملاحظتك على الفصل الثاني" or "تم تحديث المتطلبات العامة"
   - If user just approved, leave empty.

5. **intent**: Classify the user's intent using ONLY the valid intents listed below.

Write in Arabic. Be precise and concise."""

INTENT_RULES = {
    "chapter_review": (
        "Valid intents:\n"
        '- "approve": User accepts the chapters and wants to proceed\n'
        '- "modify_chapters": User wants to add, remove, rename, or reorder chapters\n'
        '- "note_only": User is adding a general note/observation or chapter-specific note WITHOUT requesting structural changes to the chapter list'
    ),
    "draft_review": (
        "Valid intents:\n"
        '- "approve": User accepts the draft as-is\n'
        '- "refine": User wants specific edits or corrections to the draft\n'
        '- "regenerate": User rejects the entire draft and wants a complete rewrite from scratch\n'
        '- "note_only": User is adding a general note/observation WITHOUT requesting changes to this draft'
    ),
}


def sync_notes(
    current_clean_requirements: str,
    user_input: str,
    context: str,
    chapter_title: str = "",
    current_chapter_note: str = "",
    chapters: list[dict] | None = None,
) -> NotesSync:
    """Sync user notes and classify intent after any interrupt response."""

    intent_rules = INTENT_RULES.get(context, INTENT_RULES["chapter_review"])

    parts = [
        f"السياق: {context}",
        f"\n{intent_rules}",
        f"\nالمتطلبات الحالية:\n{current_clean_requirements or '(فارغة)'}",
        f"\nرد اليوزر:\n{user_input}",
    ]

    # Full chapter list (for chapter_review context)
    if chapters:
        ch_lines = []
        for i, ch in enumerate(chapters):
            line = f"  [{i}] {ch['title']}"
            if ch.get("chapter_notes"):
                line += f" | ملاحظة حالية: {ch['chapter_notes']}"
            ch_lines.append(line)
        parts.append(f"\nالفصول الحالية (0-indexed):\n" + "\n".join(ch_lines))

    # Single chapter (for draft_review context)
    elif chapter_title:
        parts.append(f"\nعنوان الفصل: {chapter_title}")
        parts.append(f"الملاحظة الحالية للفصل:\n{current_chapter_note or '(فارغة)'}")

    user_content = "\n".join(parts)

    result = _structured_llm.invoke([
        SystemMessage(content=NOTES_SYNC_PROMPT),
        HumanMessage(content=user_content),
    ])
    return result


# ─── Deterministic prompt builders ────────────────────────────


def _format_chapters_block(chapters: list[dict]) -> str:
    """Build a deterministic, formatted chapter list string."""
    lines = []
    for i, ch in enumerate(chapters):
        line = f"{i+1}. {ch['title']}"
        if ch.get("description"):
            line += f"\n   → {ch['description']}"
        if ch.get("chapter_notes"):
            line += f"\n   📝 ملاحظة: {ch['chapter_notes']}"
        lines.append(line)
    return "\n".join(lines)


def generate_review_prompt(
    chapters: list[dict],
    clean_requirements: str,
    acknowledgment: str = "",
) -> str:
    """Build a chapter review prompt. Deterministic chapter list + acknowledgment."""
    numbered = _format_chapters_block(chapters)

    parts = []
    if acknowledgment:
        parts.append(acknowledgment)
    parts.append(f"هذي الفصول الحالية:\n\n{numbered}")
    if clean_requirements:
        parts.append(f"📋 المتطلبات المصفّاة:\n{clean_requirements}")
    parts.append(
        "اكتب موافق عشان نبدأ التوليد، "
        "أو اكتب التعديل اللي تبيه (حذف، إضافة، تعديل)، "
        "أو أضف ملاحظة على أي فصل:"
    )
    return "\n\n".join(parts)


def generate_draft_review_prompt(
    idx: int,
    total: int,
    chapter_title: str,
    draft: str,
    chapter_notes: str = "",
    acknowledgment: str = "",
) -> str:
    """Build a draft review prompt. Deterministic layout + acknowledgment."""
    parts = []
    if acknowledgment:
        parts.append(acknowledgment)
    parts.append(f"الفصل {idx + 1} من {total}: {chapter_title}")
    if chapter_notes:
        parts.append(f"📝 ملاحظة الفصل: {chapter_notes}")
    parts.append(draft)
    parts.append(
        "────────\n"
        "راجع المسودة. اكتب موافق وننتقل للفصل التالي، "
        "أو اكتب ملاحظاتك، أو أضف ملاحظة عامة:"
    )
    return "\n\n".join(parts)
