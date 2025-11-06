"""
Content extraction and transformation tools for creating different types of snippets
and social content from longer-form writing.
"""
from __future__ import annotations
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from storage import get_node, add_content, link_relates, NODE_DIRS, get_content_links
from dataclasses import dataclass


@dataclass
class ExtractedSnippet:
    """Represents an extracted snippet with metadata."""
    content: str
    start_pos: int
    end_pos: int
    context: str = ""
    score: float = 0.0


def extract_raw_content(
    content_id: str,
    max_length: Optional[int] = None,
    style: Optional[List[str]] = None,
    preserve_tags: bool = True,
    preserve_authors: bool = True,
) -> str:
    """
    Extract raw content from a content node, optionally truncating and preserving metadata.

    Args:
        content_id: UUID of the content node to extract from
        max_length: Maximum character count for extracted content. None = no limit.
        style: Style tags to apply to extracted content (e.g., ["snippet"])
        preserve_tags: If True, copy tags from source content
        preserve_authors: If True, copy authors from source content

    Returns:
        UUID of the newly created content node containing the extract
    """
    source = get_node(content_id)
    content_text = source.get("content", "")

    if max_length and len(content_text) > max_length:
        content_text = content_text[:max_length] + "..."

    tags = source.get("tags", []) if preserve_tags else []
    authors = source.get("authors", []) if preserve_authors else []
    style = style or ["snippet"]

    new_id = add_content(
        content=content_text,
        title=f"Extract from: {source.get('title', content_id[:8])}",
        style=style,
        tags=tags,
        authors=authors,
    )

    # Link back to source
    link_relates(new_id, "snippet_of", content_id)

    return new_id


def extract_by_paragraph(
    content_id: str,
    min_words: int = 20,
    max_snippets: Optional[int] = None,
    style: Optional[List[str]] = None,
) -> List[str]:
    """
    Extract individual paragraphs as separate snippets.

    Args:
        content_id: UUID of the content node to extract from
        min_words: Minimum word count for a paragraph to be extracted
        max_snippets: Maximum number of snippets to create. None = no limit.
        style: Style tags to apply (e.g., ["snippet"])

    Returns:
        List of UUIDs for newly created snippet nodes
    """
    source = get_node(content_id)
    content_text = source.get("content", "")
    paragraphs = [p.strip() for p in content_text.split("\n\n") if p.strip()]

    snippet_ids = []
    style = style or ["snippet"]

    for para in paragraphs:
        word_count = len(para.split())
        if word_count >= min_words:
            snippet_id = add_content(
                content=para,
                title=f"Paragraph from: {source.get('title', content_id[:8])}",
                style=style,
                tags=source.get("tags", []),
                authors=source.get("authors", []),
            )
            link_relates(snippet_id, "snippet_of", content_id)
            snippet_ids.append(snippet_id)

            if max_snippets and len(snippet_ids) >= max_snippets:
                break

    return snippet_ids


def extract_similar_sections(
    content_id: str,
    keyword: str,
    context_sentences: int = 2,
    style: Optional[List[str]] = None,
) -> List[str]:
    """
    Extract sections that contain a specific keyword or topic, with surrounding context.

    Args:
        content_id: UUID of the content node to extract from
        keyword: Keyword or phrase to search for (case-insensitive)
        context_sentences: Number of sentences before/after match to include
        style: Style tags to apply (e.g., ["snippet"])

    Returns:
        List of UUIDs for newly created snippet nodes
    """
    source = get_node(content_id)
    content_text = source.get("content", "")

    # Split into sentences
    sentences = re.split(r"(?<=[.!?])\s+", content_text)

    snippet_ids = []
    style = style or ["snippet"]
    keyword_lower = keyword.lower()

    for i, sentence in enumerate(sentences):
        if keyword_lower in sentence.lower():
            # Get context window
            start_idx = max(0, i - context_sentences)
            end_idx = min(len(sentences), i + context_sentences + 1)
            context_block = " ".join(sentences[start_idx:end_idx])

            snippet_id = add_content(
                content=context_block,
                title=f"Section on '{keyword}' from: {source.get('title', content_id[:8])}",
                style=style,
                tags=source.get("tags", []) + [keyword.lower().replace(" ", "-")],
                authors=source.get("authors", []),
            )
            link_relates(snippet_id, "snippet_of", content_id)
            snippet_ids.append(snippet_id)

    return snippet_ids


def extract_for_social_media(
    content_id: str,
    platform: str = "twitter",
    max_count: int = 5,
) -> List[str]:
    """
    Extract punchy, quotable snippets suitable for social media posts.

    Args:
        content_id: UUID of the content node to extract from
        platform: Target platform. Options: "twitter", "linkedin", "instagram"
        max_count: Maximum number of social snippets to create

    Returns:
        List of UUIDs for newly created snippet nodes
    """
    source = get_node(content_id)
    content_text = source.get("content", "")

    # Platform-specific constraints
    constraints = {
        "twitter": {"max_length": 280, "style": ["tweet", "snippet"]},
        "linkedin": {"max_length": 700, "style": ["post", "snippet"]},
        "instagram": {"max_length": 500, "style": ["post", "snippet"]},
    }

    config = constraints.get(platform, constraints["twitter"])
    max_length = config["max_length"]
    style = config["style"]

    # Split into sentences and find good candidates
    sentences = re.split(r"(?<=[.!?])\s+", content_text)

    # Heuristics for "good" social content:
    # - Contains action words or questions
    # - Not too short, not too long
    # - Ideally complete thought

    snippet_ids = []
    action_words = ["discover", "learn", "build", "create", "think", "consider", "imagine", "remember"]

    for sentence in sentences:
        if len(snippet_ids) >= max_count:
            break

        # Check if sentence is a good candidate
        sentence_lower = sentence.lower()
        is_question = "?" in sentence
        has_action = any(word in sentence_lower for word in action_words)

        if (is_question or has_action) and 20 <= len(sentence) <= max_length:
            snippet_id = add_content(
                content=sentence,
                title=f"{platform.capitalize()} snippet from: {source.get('title', content_id[:8])}",
                style=style,
                tags=source.get("tags", []) + [platform, "social-media"],
                authors=source.get("authors", []),
            )
            link_relates(snippet_id, "snippet_of", content_id)

            # Also copy any source links
            source_links = get_content_links(content_id)
            from storage import link_url
            for link in source_links:
                link_url(snippet_id, link.get("url", ""), link.get("title"), link.get("description"))

            snippet_ids.append(snippet_id)

    return snippet_ids


def combine_related_snippets(
    content_ids: List[str],
    title: str,
    style: Optional[List[str]] = None,
    separator: str = "\n\n---\n\n",
) -> str:
    """
    Combine multiple snippets into a single longer-form piece.

    Args:
        content_ids: List of content node UUIDs to combine
        title: Title for the combined content
        style: Style tags for combined content (e.g., ["blog", "post"])
        separator: Text to insert between combined snippets

    Returns:
        UUID of newly created combined content node
    """
    combined_parts = []
    all_tags = set()
    all_authors = set()

    for content_id in content_ids:
        try:
            node = get_node(content_id)
            combined_parts.append(node.get("content", ""))
            all_tags.update(node.get("tags", []))
            all_authors.update(node.get("authors", []))
        except FileNotFoundError:
            continue

    combined_content = separator.join(combined_parts)
    style = style or ["blog", "post"]

    combined_id = add_content(
        content=combined_content,
        title=title,
        style=style,
        tags=list(all_tags),
        authors=list(all_authors),
    )

    # Link all source snippets as related
    for source_id in content_ids:
        try:
            link_relates(source_id, "related_to", combined_id)
        except Exception:
            continue

    return combined_id
