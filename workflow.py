from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from graph_state import GraphState
from nodes import (
    analyze_template,
    approve_chapter,
    generate_chapter,
    human_review,
    refine_chapter,
    review_chapter,
    route_entry,
    route_after_approve,
    route_after_chapters_review,
    route_after_collect_input,
    route_after_human_review,
    save_output,
    update_chapter,
    extract_chapter_samples,
    propose_default_chapters,
    analyze_revision,
    prepare_export,
    collect_input,
)

checkpointer = InMemorySaver()


def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("analyze_template", analyze_template)
    workflow.add_node("extract_chapter_samples", extract_chapter_samples)
    workflow.add_node("review_chapter", review_chapter)
    workflow.add_node("update_chapter", update_chapter)
    workflow.add_node("generate_chapter", generate_chapter)
    workflow.add_node("human_review", human_review)
    workflow.add_node("approve_chapter", approve_chapter)
    workflow.add_node("refine_chapter", refine_chapter)
    workflow.add_node("prepare_export", prepare_export)
    workflow.add_node("save_output", save_output)
    workflow.add_node("propose_default_chapters", propose_default_chapters)
    workflow.add_node("analyze_revision", analyze_revision)
    workflow.add_node("collect_input", collect_input)

    # START يقرر المسار: تمبلت أو مقابلة ديناميكية (manual/zero_data)
    workflow.add_conditional_edges(
        START,
        route_entry,
        {
            "analyze_template": "analyze_template",
            "collect_input": "collect_input",
        },
    )

    # تمبلت → مراجعة المحاور مباشرة
    workflow.add_edge("analyze_template", "review_chapter")

    workflow.add_conditional_edges(
        "collect_input",
        route_after_collect_input,
        {
            "collect_input": "collect_input",
            "propose_default_chapters": "propose_default_chapters",
        },
    )
    workflow.add_edge("propose_default_chapters", "review_chapter")

    # مراجعة المحاور → توليد أو تعديل
    workflow.add_conditional_edges(
        "review_chapter",
        route_after_chapters_review,
        {
            "extract_chapter_samples": "extract_chapter_samples",
            "generate_chapter": "generate_chapter",
            "update_chapter": "update_chapter",
        },
    )
    workflow.add_edge("update_chapter", "review_chapter")
    workflow.add_edge("extract_chapter_samples", "generate_chapter")

    # توليد → مراجعة بشرية → موافقة أو تحسين
    workflow.add_edge("generate_chapter", "human_review")
    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "approve_chapter": "approve_chapter",
            "refine_chapter": "analyze_revision",
            "generate_chapter": "generate_chapter",
        }
    )

    workflow.add_edge("analyze_revision", "refine_chapter")


    # موافقة → الفصل الجاي أو الحفظ
    workflow.add_conditional_edges(
        "approve_chapter",
        route_after_approve,
        {
            "extract_chapter_samples": "extract_chapter_samples",
            "generate_chapter": "generate_chapter",
            "prepare_export": "prepare_export",
        },
    )
    workflow.add_edge("refine_chapter", "human_review")
    workflow.add_edge("prepare_export", "save_output")
    workflow.add_edge("save_output", END)

    return workflow.compile(checkpointer=checkpointer)