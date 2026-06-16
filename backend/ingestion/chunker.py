from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Shared splitter instance — 512-token chunks with 50-token overlap
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # characters (~512 tokens for English text)
    chunk_overlap=100,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def split_text(text: str) -> list[str]:
    """Split a long text into overlapping chunks."""
    return _splitter.split_text(text)
