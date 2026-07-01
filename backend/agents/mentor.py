from langgraph.graph import (
    StateGraph,
    END,
)

from agents.state import MentorState

from agents.mentor_nodes import (

    load_user_profile,

    submission_analysis,

    weakness_detection,

    teaching,

    remediation,

    skill_update,

    next_question,

    should_teach,

    generate_ai_practice,

    should_generate_ai_practice,
)


def build_mentor_graph():

    workflow = StateGraph(
        MentorState
    )

    workflow.add_node(
        "load_user_profile",
        load_user_profile,
    )

    workflow.add_node(
        "submission_analysis",
        submission_analysis,
    )

    workflow.add_node(
        "weakness_detection",
        weakness_detection,
    )

    workflow.add_node(
        "teaching",
        teaching,
    )

    workflow.add_node(
        "remediation",
        remediation,
    )

    workflow.add_node(
        "skill_update",
        skill_update,
    )

    # Phase 2 – AI Practice node
    workflow.add_node(
        "generate_ai_practice",
        generate_ai_practice,
    )

    workflow.add_node(
        "next_question",
        next_question,
    )

    workflow.set_entry_point(
        "load_user_profile"
    )

    workflow.add_edge(
        "load_user_profile",
        "submission_analysis",
    )

    workflow.add_edge(
        "submission_analysis",
        "weakness_detection",
    )

    workflow.add_conditional_edges(

        "weakness_detection",

        should_teach,

        {
            "remediation": "remediation",
            "teaching": "teaching",
            "skill_update": "skill_update",
        },
    )

    workflow.add_conditional_edges(
        "teaching",
        lambda state: "skill_update" if state["analysis"].correct else "remediation",
        {
            "remediation": "remediation",
            "skill_update": "skill_update"
        }
    )

    workflow.add_edge(
        "remediation",
        "skill_update",
    )

    # After skill_update: branch to AI practice (correct) or skip to next_question
    workflow.add_conditional_edges(
        "skill_update",
        should_generate_ai_practice,
        {
            "generate_ai_practice": "generate_ai_practice",
            "next_question": "next_question",
        },
    )

    workflow.add_edge(
        "generate_ai_practice",
        "next_question",
    )

    workflow.add_edge(
        "next_question",
        END,
    )

    return workflow.compile()


mentor_graph = build_mentor_graph()