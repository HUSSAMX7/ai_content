from graph_state import GraphState
from schemas import ChapterList
from llm_config import llm
from langchain_core.messages import HumanMessage, SystemMessage

from debug_brief import print_analyzed_template_chapters

_structured_llm = llm.with_structured_output(ChapterList)


def analyze_template(state: GraphState) -> dict:
    messages = [
        SystemMessage(
            content=(
                "You are an expert document analyst.\n"
                "You receive raw text that may contain a table of contents, headings, body text, "
                "and/or user instructions mixed together. Your job is to extract the full chapter structure.\n\n"

                "## Priority rule\n"
                "If a Table of Contents (TOC) exists in the text — identified by a list of numbered or titled entries "
                "with page numbers or anchor links — it is the PRIMARY source for chapter structure. "
                "Extract ALL chapters and sub-chapters from it. Do not skip any entry.\n"
                "IMPORTANT: Ignore any 'List of Figures' or 'List of Tables' sections "
                "(entries that start with words like 'صورة', 'شكل', 'جدول', or 'Figure', 'Table', 'Image' followed by a number). "
                "These are not chapters and must be excluded entirely.\n\n"

                "## Three cases:\n\n"

                "CASE A — TOC exists:\n"
                "  • Extract every entry from the TOC as a chapter (including sub-sections like 2.1, 2.2, etc.).\n"
                "  • For each chapter, scan the rest of the text for any user-provided instructions or notes "
                "that relate to that chapter (e.g., a note saying 'write an intro about generative AI' belongs to the introduction chapter).\n"
                "  • If a matching user instruction exists, use it as the chapter description.\n"
                "  • If no instruction exists for a chapter, leave the description as an empty string.\n"
                "  • Preserve the exact TOC titles and order.\n"
                "  • After mapping all TOC chapters, scan user instructions again for any chapter or section "
                "they explicitly request that does NOT exist in the TOC (e.g., a conclusion, summary, or any named section). "
                "Add each as a new chapter at the end, using the user's instruction as its description "
                "and inferring a proper title from it.\n\n"

                "CASE B — No TOC, but explicit headings exist:\n"
                "  • Use the exact heading text as the title.\n"
                "  • The description is the instructional/body text that follows the heading.\n\n"

                "CASE C — No TOC, no explicit headings (pure instructional paragraphs):\n"
                "  • Each paragraph or block of text is one chapter.\n"
                "  • Copy the full paragraph text verbatim as the description.\n"
                "  • Infer a SHORT title (1–3 words maximum) that names the core topic. "
                "The title must be a noun/concept label, NOT a phrase copied from the text.\n\n"

                "## Rules for all cases:\n"
                "  • Never merge multiple distinct sections into one chapter.\n"
                "  • Preserve the original language.\n"
                "  • Preserve the order sections appear in the source.\n"
                "  • Do not invent description content beyond what is in the source text."
            )
        ),
        HumanMessage(content=f"Template text:\n\n{state['template']}"),
    ]
    result = _structured_llm.invoke(messages)
    chapters = [{"title": c.title, "description": c.description} for c in result.chapters]
    print_analyzed_template_chapters(chapters)
    return {"chapters": chapters}