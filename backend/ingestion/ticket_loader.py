from __future__ import annotations

import csv
import io
import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# Column name aliases for common public datasets
_TITLE_KEYS = ["title", "subject", "issue_summary", "ticket_subject", "summary", "problem_statement"]
_DESC_KEYS = ["description", "body", "issue_description", "ticket_body", "details", "problem_description", "text"]
_PRIORITY_KEYS = ["priority", "ticket_priority", "urgency"]
_STATUS_KEYS = ["status", "ticket_status", "state"]
_CATEGORY_KEYS = ["category", "department", "queue", "type", "issue_type", "product", "topic"]
_RESOLUTION_KEYS = ["resolution", "solution", "answer", "agent_answer", "response", "resolution_notes"]
_TAGS_KEYS = ["tags", "labels", "tag"]


def _find_value(row: dict[str, str], keys: list[str]) -> str:
    """Case-insensitive key lookup in a CSV row dict."""
    row_lower = {k.lower(): v for k, v in row.items()}
    for key in keys:
        if key in row_lower:
            return (row_lower[key] or "").strip()
    return ""


def _normalize_priority(raw: str) -> str:
    raw = raw.lower().strip()
    if raw in ("critical", "urgent", "p1", "1"):
        return "critical"
    elif raw in ("high", "p2", "2"):
        return "high"
    elif raw in ("medium", "moderate", "normal", "p3", "3"):
        return "medium"
    elif raw in ("low", "p4", "4"):
        return "low"
    return "medium"


def _normalize_status(raw: str) -> str:
    raw = raw.lower().strip()
    if raw in ("open", "new", "active"):
        return "open"
    elif raw in ("in_progress", "in progress", "pending", "working"):
        return "in_progress"
    elif raw in ("resolved", "solved", "fixed", "answered"):
        return "resolved"
    elif raw in ("closed", "complete", "completed", "done"):
        return "closed"
    return "open"


class TicketLoader:
    """
    Universal CSV loader that auto-maps column names from common public
    support ticket datasets to our unified ticket schema.
    """

    def parse_csv(
        self, text: str, source_dataset: str = "unknown"
    ) -> list[dict[str, Any]]:
        """Parse CSV text and return list of ticket dicts ready for DB insert."""
        reader = csv.DictReader(io.StringIO(text))
        records: list[dict[str, Any]] = []
        seen_numbers: set[str] = set()

        for i, row in enumerate(reader):
            try:
                title = _find_value(row, _TITLE_KEYS) or f"Ticket from {source_dataset}"
                if not title:
                    continue

                ticket_number = f"{source_dataset[:8].upper()}-{i+1:06d}"
                if ticket_number in seen_numbers:
                    continue
                seen_numbers.add(ticket_number)

                raw_priority = _find_value(row, _PRIORITY_KEYS)
                raw_status = _find_value(row, _STATUS_KEYS)
                raw_tags = _find_value(row, _TAGS_KEYS)

                records.append({
                    "ticket_number": ticket_number,
                    "title": title[:500],
                    "description": _find_value(row, _DESC_KEYS) or None,
                    "resolution": _find_value(row, _RESOLUTION_KEYS) or None,
                    "category": _find_value(row, _CATEGORY_KEYS) or None,
                    "priority": _normalize_priority(raw_priority) if raw_priority else "medium",
                    "status": _normalize_status(raw_status) if raw_status else "open",
                    "tags": [t.strip() for t in raw_tags.split(",") if t.strip()] if raw_tags else [],
                    "source_dataset": source_dataset,
                })
            except Exception as e:
                logger.warning(f"Skipping row {i}: {e}")
                continue

        logger.info(f"Parsed {len(records)} tickets from '{source_dataset}'")
        return records
