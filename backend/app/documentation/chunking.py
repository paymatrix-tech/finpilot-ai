from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChunkDraft:
    content: str
    metadata: dict[str, Any]


def chunk_markdown(
    content: str,
    *,
    document_name: str,
    category: str,
    max_chars: int = 1200,
) -> list[ChunkDraft]:
    """Split markdown into section-sized chunks for embedding."""
    normalized = content.strip()
    if not normalized:
        return []

    sections = _split_markdown_sections(normalized)
    drafts: list[ChunkDraft] = []
    chunk_index = 0

    for section_index, (heading, body) in enumerate(sections):
        section_text = _join_section(heading, body)
        pieces = _split_oversized_text(section_text, max_chars=max_chars)
        for piece_index, piece in enumerate(pieces):
            drafts.append(
                ChunkDraft(
                    content=piece,
                    metadata={
                        "document_name": document_name,
                        "category": category,
                        "section_index": section_index,
                        "section_heading": heading,
                        "chunk_index": chunk_index,
                        "piece_index": piece_index,
                    },
                )
            )
            chunk_index += 1

    return drafts


def _split_markdown_sections(content: str) -> list[tuple[str | None, str]]:
    lines = content.splitlines()
    sections: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current_body: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_heading is not None or current_body:
                sections.append((current_heading, "\n".join(current_body).strip()))
            current_heading = line[3:].strip()
            current_body = []
            continue
        if current_heading is None and not sections and not current_body and line.startswith("# "):
            current_heading = line[2:].strip()
            continue
        current_body.append(line)

    if current_heading is not None or current_body:
        sections.append((current_heading, "\n".join(current_body).strip()))

    if not sections:
        return [(None, content)]

    return sections


def _join_section(heading: str | None, body: str) -> str:
    if heading and body:
        return f"## {heading}\n\n{body}".strip()
    if heading:
        return f"## {heading}".strip()
    return body.strip()


def _split_oversized_text(text: str, *, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not paragraphs:
        return [text[:max_chars]]

    pieces: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            pieces.append(current)
        if len(paragraph) <= max_chars:
            current = paragraph
            continue
        start = 0
        while start < len(paragraph):
            pieces.append(paragraph[start : start + max_chars])
            start += max_chars
        current = ""

    if current:
        pieces.append(current)
    return pieces
