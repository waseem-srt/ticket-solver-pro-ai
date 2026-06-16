from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from agents.nodes import (
    AgentState,
    node_evaluate_confidence,
    node_generate_rag_response,
    node_generate_web_response,
    node_rag_retrieve,
    node_web_search,
    route_after_confidence,
)


def build_query_graph() -> StateGraph:
    """
    Builds the LangGraph workflow:

        START
          ↓
        rag_retrieve         (ChromaDB query)
          ↓
        evaluate_confidence  (threshold check)
          ↓ (conditional)
        ┌─────────────────────────┐
        │                         │
      generate_rag           web_search
        │                         ↓
        │                 generate_web_response
        │                         │
        └────────────► END ◄──────┘
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("rag_retrieve", node_rag_retrieve)
    workflow.add_node("evaluate_confidence", node_evaluate_confidence)
    workflow.add_node("web_search", node_web_search)
    workflow.add_node("generate_rag", node_generate_rag_response)
    workflow.add_node("generate_web", node_generate_web_response)

    # Edges
    workflow.add_edge(START, "rag_retrieve")
    workflow.add_edge("rag_retrieve", "evaluate_confidence")

    # Conditional routing
    workflow.add_conditional_edges(
        "evaluate_confidence",
        route_after_confidence,
        {"web_search": "web_search", "generate_rag": "generate_rag"},
    )

    workflow.add_edge("web_search", "generate_web")
    workflow.add_edge("generate_rag", END)
    workflow.add_edge("generate_web", END)

    return workflow


@lru_cache(maxsize=1)
def get_compiled_graph():
    """Returns the compiled LangGraph (cached singleton)."""
    graph = build_query_graph()
    return graph.compile()


def run_query(
    query: str,
    history: list[dict] | None = None,
) -> dict:
    """
    Run the full query pipeline synchronously.
    Returns dict with 'response', 'citations', 'needs_web_search', 'confidence'.
    """
    app = get_compiled_graph()
    initial_state: AgentState = AgentState({
        "query": query,
        "history": history or [],
        "context_chunks": [],
        "confidence": 1.0,
        "needs_web_search": False,
        "web_results": [],
        "response": "",
        "citations": [],
        "kb_empty": False,
    })
    final_state = app.invoke(initial_state)
    return {
        "response": final_state.get("response", ""),
        "citations": final_state.get("citations", []),
        "needs_web_search": final_state.get("needs_web_search", False),
        "confidence": final_state.get("confidence", 1.0),
    }
