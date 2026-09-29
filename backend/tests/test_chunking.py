from app.documentation.chunking import chunk_markdown


def test_chunk_markdown_splits_on_headings() -> None:
    content = """# Retry policy

Intro paragraph.

## Retry allowed

Line one.

## Do not retry

Never retry fraud.
"""
    chunks = chunk_markdown(
        content,
        document_name="retry-policy.md",
        category="policy",
    )
    assert len(chunks) >= 2
    assert any("Retry allowed" in chunk.content for chunk in chunks)
    assert any("Do not retry" in chunk.content for chunk in chunks)
    assert chunks[0].metadata["document_name"] == "retry-policy.md"
    assert chunks[0].metadata["category"] == "policy"


def test_chunk_markdown_splits_large_sections() -> None:
    paragraph = "word " * 400
    content = f"# Title\n\n## Section\n\n{paragraph}"
    chunks = chunk_markdown(
        content,
        document_name="large.md",
        category="general",
        max_chars=500,
    )
    assert len(chunks) > 1
    assert all(len(chunk.content) <= 500 for chunk in chunks)
