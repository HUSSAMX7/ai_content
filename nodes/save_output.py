from graph_state import GraphState
from langgraph.types import interrupt

def save_output(state: GraphState) -> dict:

    final_content = state["final_content"]

    file_name = interrupt("ادخل اسم الملف الذي تريد حفظ النتيجة فيه ؟")
    

    with open(f"{file_name}.md", "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"\nSaved output to: {file_name}.md")
    return {}



