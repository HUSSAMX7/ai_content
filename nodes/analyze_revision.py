from langchain_core.messages import HumanMessage, SystemMessage

from graph_state import GraphState
from llm_config import llm


def analyze_revision(state: GraphState) -> dict:
    draft = state["draft"]
    raw_feedback = state.get("raw_feedback", "")
    past_analysis = state.get("text_analysis", [])
    past_notes = state.get("feedback_notes", [])

    round_num = len(past_analysis) + 1

    history_block = ""
    if past_analysis:
        history_block = "Previous rounds history:\n"
        for i, (ta, fn) in enumerate(zip(past_analysis, past_notes)):
            history_block += (
                f"\nTEXT_ANALYSIS{i+1}: {ta}\n"
                f"FEEDBACK_NOTES{i+1}: {fn}\n"
            )
        history_block += "\n"

    system_prompt = (
        "You are a document revision analyst.\n"
        "You receive a chapter draft and a reviewer's raw feedback.\n\n"
        "Your job is to produce two things:\n\n"
        f"1. TEXT_ANALYSIS{round_num}: An objective description of the current draft.\n"
        "   Include: approximate word count, number of sections, "
        "which section is longest, overall structure.\n\n"
        f"2. FEEDBACK_NOTES{round_num}: A clear, structured problem statement derived from the raw feedback.\n"
        "   Include: what exactly is wrong, which section is affected, "
        "what the reviewer wants, and what must NOT be touched.\n\n"
        "If there is revision history, factor it in — do not undo previous fixes.\n\n"
        "Output format strictly (one line each):\n"
        f"TEXT_ANALYSIS{round_num}: ...\n"
        f"FEEDBACK_NOTES{round_num}: ..."
    )

    user_prompt = (
        f"{history_block}"
        f"Current draft:\n{draft}\n\n"
        f"Reviewer raw feedback:\n{raw_feedback}"
    )

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    response = llm.invoke(messages)

    ta_key = f"TEXT_ANALYSIS{round_num}:"
    fn_key = f"FEEDBACK_NOTES{round_num}:"

    text_analysis = ""
    feedback_notes = ""
    current_key = None
    buffer = []

    for line in response.content.splitlines():
        if line.startswith(ta_key):
            current_key = "ta"
            buffer = [line.replace(ta_key, "").strip()]
        elif line.startswith(fn_key):
            if current_key == "ta":
                text_analysis = " ".join(buffer).strip()
            current_key = "fn"
            buffer = [line.replace(fn_key, "").strip()]
        else:
            if current_key:
                buffer.append(line.strip())

    if current_key == "fn":
        feedback_notes = " ".join(buffer).strip()
    elif current_key == "ta":
        text_analysis = " ".join(buffer).strip()

    return {
        "text_analysis": past_analysis + [text_analysis],
        "feedback_notes": past_notes + [feedback_notes],
    }