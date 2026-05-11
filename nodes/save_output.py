from graph_state import GraphState


def save_output(state: GraphState) -> dict:

    final_content = state["final_content"]


    with open("output.md", "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"\nSaved output to: output.md")
    return {}
