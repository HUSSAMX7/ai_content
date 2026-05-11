from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import interrupt

from graph_state import GraphState
from llm_config import llm, llm_fast
from schemas import InterviewAssimilation


ANALYST_INTERVIEW_PROMPT = """You are an expert and intelligent requirements analyst. You are conducting an interview to gather documentation requirements.

Your Golden Rules:
1. Acknowledge the response: Start your reply with a brief phrase confirming your understanding of the user's last response (e.g., in Arabic: "تمام، تم تعديل الاسم لـ..." or "ملاحظة ممتازة بخصوص...").
2. Fill the gaps: Read the memo, identify the most important missing information, and ask exactly one question about it.
3. Contextual Intelligence: If the user corrects previous information, acknowledge the correction and confirm the update.
4. Avoid Redundancy: Do not repeat questions that have already been answered in the memo.
Speak in Arabic with a professional and friendly tone."""

REQUIREMENTS_EXTRACTOR_PROMPT = """You are responsible for accurately and professionally managing and filtering project requirements.

Your Primary Tasks:
1) Update the Log (updated_memo): Add new information to the full requirements memo, maintaining the conversation context and technical notes that assist you during the interview.
2) Extract Clean Requirements (clean_requirements): This is the most critical output. Extract only verified and final facts in a direct bullet-point format.
    - Strictly forbidden to write phrases like "The user has not decided yet" or "The question was skipped."
    - If clear information is available, write it. If not, leave this field completely empty for that point.
    - This field must be ready as input for the "Chapter Generation" node without any human intervention.

3) Completion Logic (interview_done):
    - Do not terminate the interview automatically.
    - Set the value to True ONLY if you detect an explicit termination keyword in Arabic such as: (خلاص، انتهينا، ابدأ الكتابة، موافق، تم).
    - Otherwise, always set it to False."""

requirements_extractor_llm = llm.with_structured_output(InterviewAssimilation)


def next_question(memo: str, last_reply: str) -> str:
    """Analyze the memo gaps and generate the next probing question."""

    if not memo.strip():
        context = "START OF INTERVIEW: No information gathered yet. Greet the user and ask for the topic and purpose immediately. in Saudi salng"
    else:
        context = (
            "Current Memo:\n"
            f"```\n{memo}\n```\n\n"
            f"Last User Reply: {last_reply}"
        )
    
    r = llm.invoke([
        SystemMessage(content=ANALYST_INTERVIEW_PROMPT),
        HumanMessage(content=context),
    ])
    return (r.content or "").strip()

def sync_requirements_state(memo: str, question: str, answer: str) -> tuple[str, str, bool]:
    """Sync the user's answer into both the raw log and clean requirements."""

    result = requirements_extractor_llm.invoke([
        SystemMessage(content=REQUIREMENTS_EXTRACTOR_PROMPT),
        HumanMessage(content=f"Previous Memo: {memo}\nQuestion: {question}\nLast Answer: {answer}")
    ])

    return (
        result.updated_memo.strip(), 
        result.clean_requirements.strip(), 
        bool(result.interview_done)
    )


def collect_input(state: GraphState) -> dict:
    memo = state.get("requirements_memo") or ""
    logs = list(state.get("interview_logs") or [])
    last_reply = logs[-1]["answer"] if logs else ""

    question = next_question(memo, last_reply)
    
    user_reply = interrupt(question)
    user_reply_str = str(user_reply).strip()

    new_memo, clean_reqs, done = sync_requirements_state(memo, question, user_reply_str)
    
    new_logs = logs + [{"question": question, "answer": user_reply_str}]

    if done:
        return {
            "requirements_memo": new_memo,        
            "clean_requirements": clean_reqs,    
            "interview_logs": new_logs,
            "action": "interview_complete",
        }

    return {
        "requirements_memo": new_memo,
        "clean_requirements": clean_reqs,
        "interview_logs": new_logs,
        "action": "continue_interview",
    }