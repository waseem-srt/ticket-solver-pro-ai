from __future__ import annotations

import logging
from typing import Any, TypedDict

from agents.web_search import format_search_results, web_search
from rag.generator import get_llm_generator
from rag.prompts import (
    CONFIDENCE_CHECK_PROMPT,
    RAG_SYSTEM_PROMPT,
    WEB_SEARCH_SYSTEM_PROMPT,
)
from rag.retriever import RAGRetriever, RetrievedChunk

logger = logging.getLogger(__name__)


# ── Graph State ───────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    query: str
    history: list[dict]
    context_chunks: list
    confidence: float
    needs_web_search: bool
    web_results: list[dict]
    response: str
    citations: list[dict]
    kb_empty: bool


# ── Node functions ─────────────────────────────────────────────────────────────

def node_rag_retrieve(state: AgentState) -> AgentState:
    """Retrieve relevant chunks from ChromaDB."""
    retriever = RAGRetriever()
    query = state.get("query", "")
    chunks: list[RetrievedChunk] = retriever.retrieve(query)

    min_distance = min((c.distance for c in chunks), default=1.0)

    state["context_chunks"] = chunks
    state["confidence"] = min_distance
    state["kb_empty"] = retriever.is_knowledge_base_empty()
    return state


def node_evaluate_confidence(state: AgentState) -> AgentState:
    """Determine if retrieved context is sufficient or if web search is needed."""
    chunks: list[RetrievedChunk] = state.get("context_chunks", [])
    kb_empty: bool = state.get("kb_empty", False)

    if kb_empty or not chunks:
        state["needs_web_search"] = True
        return state

    # Check if any chunk meets the confidence threshold
    confident_chunks = [c for c in chunks if c.is_confident]
    if not confident_chunks:
        state["needs_web_search"] = True
        logger.info(
            f"Low confidence (min distance={state.get('confidence', 1.0):.3f}), "
            f"falling back to web search"
        )
    else:
        state["needs_web_search"] = False

    return state


def node_web_search(state: AgentState) -> AgentState:
    """Perform DuckDuckGo web search as fallback."""
    query = state.get("query", "")
    results = web_search(query)
    state["web_results"] = results
    return state


def node_generate_rag_response(state: AgentState) -> AgentState:
    """Generate response from RAG context."""
    query = state.get("query", "")
    chunks: list[RetrievedChunk] = state.get("context_chunks", [])
    history = state.get("history", [])

    context = "\n\n---\n\n".join(
        [f"[{c.metadata.get('ticket_number', c.metadata.get('filename', 'doc'))}]\n{c.text}"
         for c in chunks]
    )
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    llm = get_llm_generator()
    try:
        response = llm.generate(
            system_prompt=system_prompt,
            user_message=query,
            history=history,
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        response = "I apologize, but I encountered an error generating a response. Please try again."

    state["response"] = response
    state["citations"] = []
    return state


def node_generate_web_response(state: AgentState) -> AgentState:
    """Generate response from web search results with citations."""
    query = state.get("query", "")
    web_results: list[dict] = state.get("web_results", [])
    history = state.get("history", [])

    if not web_results:
        state["response"] = (
            "I couldn't find relevant information in the internal knowledge base "
            "and the web search returned no results. Please try rephrasing your question."
        )
        state["citations"] = []
        return state

    context = format_search_results(web_results)
    system_prompt = WEB_SEARCH_SYSTEM_PROMPT.format(context=context)

    llm = get_llm_generator()
    try:
        response = llm.generate(
            system_prompt=system_prompt,
            user_message=query,
            history=history,
        )
    except Exception as e:
        logger.error(f"LLM web generation failed: {e}")
        response = "I encountered an error generating a response from web results."

    state["response"] = response
    state["citations"] = [
        {"title": r["title"], "url": r["url"], "snippet": r["snippet"][:200]}
        for r in web_results
    ]
    return state


# ── Routing ───────────────────────────────────────────────────────────────────

def route_after_confidence(state: AgentState) -> str:
    """Conditional edge: route to web search or RAG generation."""
    return "web_search" if state.get("needs_web_search") else "generate_rag"
