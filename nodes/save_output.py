import os
from pathlib import Path
from graph_state import GraphState
from langgraph.types import interrupt

OUTPUT_DIR = Path("generated_file")


def save_output(state: GraphState) -> dict:

    final_content = state["final_content"]

    file_name = interrupt("ادخل اسم الملف الذي تريد حفظ النتيجة فيه ؟")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sotred_file_name = OUTPUT_DIR / f"{file_name}.md"

    with open(sotred_file_name, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"\nSaved output to: {sotred_file_name}")
    return {}

