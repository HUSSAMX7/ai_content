from langchain_core.messages import HumanMessage, SystemMessage
from schemas import ReviewDecision
from llm_config import llm




_structured_llm = llm.with_structured_output(ReviewDecision)


def _classify_response(user_response: str) -> str:
    messages = [
        SystemMessage(
            content=(
                "You are a text classifier. Determine the user's intent from their reply to a written chapter.\n\n"
                "action = approve → reply expresses approval or satisfaction "
                "(e.g. ok, good, great, perfect, approved, looks good, nice, excellent, fine, correct, yes, suitable, accepted, ممتاز, موافق, تمام, جيد...)\n\n"
                "action = regenerate → reply asks for a COMPLETE rewrite from scratch, "
                "rejecting the entire text and wanting a fully different version "
                "(e.g. rewrite completely, start over, I don't like it at all, change everything, "
                "أعد الكتابة, غيره بالكامل, ما عجبني, أعد توليده, من الصفر, كله غلط, اكتب غيره...)\n\n"
                "action = refine → reply asks for specific changes, edits, or corrections to the existing text "
                "(anything that is not full approval and not a request to start completely over)"
            )
        ),
        HumanMessage(content=f'User reply: "{user_response}"'),
    ]
    result: ReviewDecision = _structured_llm.invoke(messages)
    return result.action
