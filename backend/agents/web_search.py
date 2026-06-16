from __future__ import annotations

import logging
from typing import Any

from duckduckgo_search import DDGS

from core.config import settings

logger = logging.getLogger(__name__)


def web_search(query: str) -> list[dict[str, str]]:
    """
    Perform a DuckDuckGo web search and return structured results.
    Returns list of {title, url, snippet} dicts.
    Falls back to empty list on error.
    """
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    max_results=settings.web_search_max_results,
                    safesearch="moderate",
                )
            )
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in results
        ]
    except Exception as e:
        logger.warning(f"Web search failed for query '{query}': {e}")
        return []


def format_search_results(results: list[dict[str, str]]) -> str:
    """Format search results as a numbered context string with citations."""
    if not results:
        return "No web search results available."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[Source {i}] {r['title']}")
        lines.append(f"URL: {r['url']}")
        lines.append(f"Content: {r['snippet']}")
        lines.append("")
    return "\n".join(lines)
