import re

from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm




def prepare_export(state: GraphState) -> dict:
    chapters = state["generated_chapters"]
    raw = "\n\n".join(chapters)

    system_prompt = (
        "Role: Professional Document Architect & Formatting Expert.\n"
        "Objective: Your sole mission is to take the provided raw content and transform it into a highly structured, professional, and visually organized document.\n"
        "\n"
        "Strict Constraints (The Golden Rules):\n"
        "\n"
        "Zero Content Alteration: Do NOT rewrite, summarize, paraphrase, or change any words. Keep the vocabulary and technical terms exactly as they appear in the source text.\n"
        "\n"
        "Structural Enhancement ONLY: Your work is limited to organization (Headings, Subheadings, Bullet points, Tables, and Numbered lists).\n"
        "\n"
        "Logical Flow: Arrange the existing text into a logical sequence that makes it 'Presentation-Ready' without adding external information.\n"
        "\n"
        "No Conversational Filler: Do not explain what you did. Do not say 'Here is your document.' Output the formatted content immediately.\n"
        "\n"
        "Heading rules (mandatory):\n"
        "- For each chapter or section title, use exactly ONE Markdown heading line for that title.\n"
        "- Never duplicate the same title at two heading levels in a row (forbidden: '# مقدمة' then immediately '## مقدمة') and if your find dulcate title remove it from the output.\n"
        "- Never put the section title again as a plain line of text right after its heading (forbidden: '# مقدمة' then a line that is only the word 'مقدمة'). The heading line is enough.\n"
        "- If the source already has a heading, keep a single appropriate level (H2 or H3) for that section, not both.\n"
        
        "\n"
        "Do NOT use horizontal rules: never output a line that is only '---' or '***' or '___'. Separate sections with blank lines only.\n"
        "\n"
        "Formatting Guidelines:\n"
        "\n"
        "Use Markdown for all styling (Bold for emphasis, H1/H2/H3 for hierarchy).\n"
        "\n"
        "Use Tables if the data contains comparisons or structured parameters.\n"
        "\n"
        "Use Blockquotes (>) for key highlights or important notes within the text.\n"
        "\n"
        "Ensure a clean 'White Space' strategy to make the document easy to scan.\n"
        "\n"
        "Task: Analyze the provided input and output the 'Architected' version of it while maintaining 100% verbal integrity.\n"
    )

    user_prompt = f"Input:\n{raw}\n"
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    response = llm.invoke(messages)
    out = response.content

    return {"final_content": out}
