from __future__ import annotations
import json
import os
from typing import Any, Optional, List, Dict
from mcp.server.fastmcp import FastMCP
from storage import (
    add_content,
    add_tag,
    add_style,
    add_author,
    add_link,
    link_relates,
    link_tag,
    link_author,
    link_url,
    get_node,
    get_content_links,
)
from search import search, rebuild_index
from content_tools import (
    extract_raw_content,
    extract_by_paragraph,
    extract_similar_sections,
    extract_for_social_media,
    combine_related_snippets,
)


def _ensure_path(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return path or "/mcp"


HTTP_HOST = os.environ.get("MCP_HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.environ.get("MCP_HTTP_PORT", "8000"))
HTTP_PATH = _ensure_path(os.environ.get("MCP_HTTP_PATH", "/mcp"))

mcp = FastMCP("snippets_manager", host=HTTP_HOST, port=HTTP_PORT, streamable_http_path=HTTP_PATH)


@mcp.tool(
    title="Add content",
    description="""Create a new content node (long-form or snippet) and index it for search.

    Parameters:
    - content (str, required): The full text body of the content. Can be any length from a tweet to a full chapter.
    - title (str, optional): A human-readable title for the content. Defaults to None.
    - date (str, optional): ISO8601 datetime string (e.g., "2025-11-05T12:34:56Z"). Defaults to current UTC time.
    - style (list[str], optional): List of style identifiers. Must be one or more of: "chapter", "blog", "post", "snippet", "tweet". Defaults to empty list.
    - tags (list[str], optional): List of tag names. Tags will be automatically normalized to lowercase with dashes replacing spaces/punctuation. Defaults to empty list.
    - authors (list[str], optional): List of author names or slugs. Authors will be created if they don't exist. Defaults to empty list.

    Returns: UUID string of the newly created content node (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890").

    Example usage:
    - Short snippet: content="Focus on user needs", style=["snippet"], tags=["product-management"]
    - Blog post: content="...", title="Getting Started with MCP", style=["blog", "post"], authors=["jane-doe"], tags=["mcp", "tutorial"]
    """
)
async def tool_add_content(
    content: str,
    title: Optional[str] = None,
    date: Optional[str] = None,
    style: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    authors: Optional[List[str]] = None,
) -> str:
    return add_content(content, title, date, style, tags, authors)


@mcp.tool(
    title="Add tag",
    description="""Create or return a tag node by name.

    Parameters:
    - name (str, required): Tag name. Will be automatically normalized to lowercase with dashes replacing spaces/punctuation (e.g., "Machine Learning" -> "machine-learning").

    Returns: Slugified tag ID (str) that can be used to reference this tag in filters and links.

    Note: If a tag with this normalized name already exists, returns the existing tag ID. Tags are idempotent.
    """
)
async def tool_add_tag(name: str) -> str:
    return add_tag(name)


@mcp.tool(
    title="Add style",
    description="""Register a writing style node.

    Parameters:
    - name (str, required): Style name. Must be one of the predefined styles: "chapter", "blog", "post", "snippet", "tweet".

    Returns: Slugified style ID (str).

    Raises: ValueError if the style name is not in the allowed list.

    Note: Styles help categorize content by format and length. Use multiple styles on a single content node if it fits multiple categories.
    """
)
async def tool_add_style(name: str) -> str:
    return add_style(name)


@mcp.tool(
    title="Add author",
    description="""Create or return an author node with optional social media handles.

    Parameters:
    - name (str, required): Author's full name (e.g., "Jane Doe"). Will be slugified for use as ID.
    - linkedin_username (str, optional): LinkedIn username without URL (e.g., "janedoe"). Defaults to empty string.
    - twitter_username (str, optional): Twitter/X handle without @ symbol (e.g., "janedoe"). Defaults to empty string.
    - substack_username (str, optional): Substack username (e.g., "janedoe"). Defaults to empty string.
    - reddit_username (str, optional): Reddit username without u/ prefix (e.g., "janedoe"). Defaults to empty string.

    Returns: Slugified author ID (str) that can be used to reference this author.

    Note: If an author with this normalized name already exists, returns the existing author ID. Authors are idempotent.
    """
)
async def tool_add_author(
    name: str,
    linkedin_username: str = "",
    twitter_username: str = "",
    substack_username: str = "",
    reddit_username: str = "",
) -> str:
    return add_author(name, linkedin_username, twitter_username, substack_username, reddit_username)


@mcp.tool(
    title="Add link",
    description="""Create or return a link (URL) node.

    Parameters:
    - url (str, required): The full URL (e.g., "https://example.com/article"). URL is used to generate a unique identifier.
    - title (str, optional): Human-readable title for the link. Defaults to None.
    - description (str, optional): Brief description of what the link contains. Defaults to None.

    Returns: Slugified link ID (str) that can be used to reference this URL.

    Note: If a link with this URL already exists, returns the existing link ID. Links are idempotent.
    Use link_url tool to associate this link with content nodes.
    """
)
async def tool_add_link(url: str, title: Optional[str] = None, description: Optional[str] = None) -> str:
    return add_link(url, title, description)


@mcp.tool(
    title="Link content relates",
    description="""Create a relationship edge between two content nodes.

    Parameters:
    - src_content_id (str, required): UUID of the source content node.
    - relation_type (str, required): Type of relationship. Must be one of: "snippet_of" (source is a snippet of destination), "related_to" (general relationship).
    - dst_content_id (str, required): UUID of the destination content node.

    Returns: "ok" on success.

    Example usage:
    - Mark snippet: link_relates(snippet_uuid, "snippet_of", parent_article_uuid)
    - Related content: link_relates(content_a_uuid, "related_to", content_b_uuid)

    Note: These relationships are directional. For "snippet_of", the source is the smaller piece extracted from the destination.
    """
)
async def tool_link_relates(src_content_id: str, relation_type: str, dst_content_id: str) -> str:
    link_relates(src_content_id, relation_type, dst_content_id)
    return "ok"


@mcp.tool(
    title="Link tag",
    description="""Attach a tag to a content node.

    Parameters:
    - content_id (str, required): UUID of the content node to tag.
    - tag_slug (str, required): Tag name or slug. Will be normalized automatically. If tag doesn't exist, it will be created.

    Returns: "ok" on success.

    Note: Multiple tags can be attached to the same content node by calling this tool multiple times.
    """
)
async def tool_link_tag(content_id: str, tag_slug: str) -> str:
    link_tag(content_id, tag_slug)
    return "ok"


@mcp.tool(
    title="Link author",
    description="""Attach an author to a content node.

    Parameters:
    - content_id (str, required): UUID of the content node.
    - author_slug (str, required): Author name or slug. Will be normalized automatically. If author doesn't exist, it will be created.

    Returns: "ok" on success.

    Note: Multiple authors can be attached to the same content node (co-authorship) by calling this tool multiple times.
    """
)
async def tool_link_author(content_id: str, author_slug: str) -> str:
    link_author(content_id, author_slug)
    return "ok"


@mcp.tool(
    title="Link URL",
    description="""Associate a URL with a content node.

    Parameters:
    - content_id (str, required): UUID of the content node.
    - url (str, required): The full URL to associate (e.g., "https://example.com/article").
    - title (str, optional): Human-readable title for the link. Defaults to None.
    - description (str, optional): Brief description of the linked resource. Defaults to None.

    Returns: "ok" on success.

    Note: A link node is automatically created if it doesn't exist. Multiple URLs can be attached to the same content node.
    Use this to track source URLs, reference materials, or related web resources for a piece of content.
    """
)
async def tool_link_url(content_id: str, url: str, title: Optional[str] = None, description: Optional[str] = None) -> str:
    link_url(content_id, url, title, description)
    return "ok"


@mcp.tool(
    title="Search content",
    description="""Search and filter content nodes with full-text query and metadata filters.

    Parameters:
    - query (str, optional): Free-text search query. Searches title and content fields with TF-IDF ranking. Defaults to None (no text filtering).
    - filters (dict, optional): Dictionary containing filter criteria. Supported keys:
        * "style": list[str] - Filter by writing style (e.g., ["blog", "post"])
        * "tag": list[str] - Filter by tag slugs (e.g., ["machine-learning", "ai"])
        * "author": list[str] - Filter by author slugs (e.g., ["jane-doe"])
        * "title": str - Substring match in title field
        * "content": str - Substring match in content field
        * "relates": list[str] - Filter by content IDs that have relationships with these IDs
    - sort (str, optional): Sort order. Must be one of: "relevance" (TF-IDF score, requires query), "date" (newest first), "random" (shuffled). Defaults to "relevance".
    - page (int, optional): 1-based page number for pagination. Defaults to 1.
    - page_size (int, optional): Number of results per page. Defaults to 10.
    - seed (int, optional): Random seed for stable "random" sort order. Only used when sort="random". Defaults to None.

    Returns: JSON string with structure:
    {
        "items": [list of content node objects with full data],
        "total": total count of matching items,
        "page": current page number,
        "page_size": items per page
    }

    Example usage:
    - Find all blog posts: filters={"style": ["blog"]}
    - Search with tag filter: query="machine learning", filters={"tag": ["ai", "tutorial"]}
    - Random snippets: filters={"style": ["snippet"]}, sort="random", seed=42
    """
)
async def tool_search(
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    sort: str = "relevance",
    page: int = 1,
    page_size: int = 10,
    seed: Optional[int] = None,
) -> str:
    filters_dict = filters if filters else {}
    res = search(query, filters_dict, sort=sort, page=page, page_size=page_size, seed=seed)
    return json.dumps(res)


@mcp.tool(
    title="Get node",
    description="""Retrieve a single node by ID or slug.

    Parameters:
    - node_id (str, required): Node identifier. Can be:
        * Content UUID (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        * Tag slug (e.g., "machine-learning")
        * Author slug (e.g., "jane-doe")
        * Style slug (e.g., "blog")
        * Link slug (generated from URL)

    Returns: JSON string containing the full node object with all fields. For content nodes, includes associated links.

    Raises: FileNotFoundError if node_id doesn't match any existing node.

    Note: This returns the raw node data. Use search tool for filtered queries across multiple nodes.
    """
)
async def tool_get_node(node_id: str) -> str:
    node = get_node(node_id)
    # If it's a content node, include associated links
    if node.get("type") == "content":
        links = get_content_links(node_id)
        node["links"] = links
    return json.dumps(node)


@mcp.tool(
    title="Reindex",
    description="""Rebuild the full-text search index from scratch.

    Parameters: None

    Returns: "ok" on success.

    Use cases:
    - After bulk imports of content nodes
    - If search results seem out of sync with actual content
    - After manual file system modifications

    Note: This operation scans all content nodes and rebuilds the inverted index, doc lengths, and metadata cache.
    The process is safe and idempotent - it won't affect your content nodes, only the search index files.
    """
)
async def tool_reindex() -> str:
    rebuild_index()
    return "ok"


# Content extraction and transformation tools

@mcp.tool(
    title="Extract raw content",
    description="""Extract raw content from a source node, with optional truncation and metadata preservation.

    Parameters:
    - content_id (str, required): UUID of the source content node to extract from.
    - max_length (int, optional): Maximum character count. Content will be truncated with "..." if exceeded. None = no limit. Defaults to None.
    - style (list[str], optional): Style tags for the extracted content (e.g., ["snippet"]). Defaults to ["snippet"].
    - preserve_tags (bool, optional): If True, copies tags from source content. Defaults to True.
    - preserve_authors (bool, optional): If True, copies authors from source content. Defaults to True.

    Returns: UUID of the newly created content node containing the extract.

    Use cases:
    - Create a shortened version of long-form content
    - Preserve the full text with different metadata
    - Generate preview snippets

    Note: Automatically creates a "snippet_of" relationship to the source content.
    """
)
async def tool_extract_raw_content(
    content_id: str,
    max_length: Optional[int] = None,
    style: Optional[List[str]] = None,
    preserve_tags: bool = True,
    preserve_authors: bool = True,
) -> str:
    return extract_raw_content(content_id, max_length, style, preserve_tags, preserve_authors)


@mcp.tool(
    title="Extract by paragraph",
    description="""Break down content into individual paragraph snippets.

    Parameters:
    - content_id (str, required): UUID of the source content node to extract from.
    - min_words (int, optional): Minimum word count for a paragraph to be extracted. Filters out very short paragraphs. Defaults to 20.
    - max_snippets (int, optional): Maximum number of snippets to create. None = extract all qualifying paragraphs. Defaults to None.
    - style (list[str], optional): Style tags to apply to extracted snippets. Defaults to ["snippet"].

    Returns: JSON array of UUIDs for the newly created snippet nodes.

    Use cases:
    - Convert a blog post into individual talking points
    - Create a collection of standalone quotes
    - Break down documentation into atomic units

    Note: Each snippet automatically gets a "snippet_of" relationship to the source. Tags and authors are preserved from source.
    """
)
async def tool_extract_by_paragraph(
    content_id: str,
    min_words: int = 20,
    max_snippets: Optional[int] = None,
    style: Optional[List[str]] = None,
) -> str:
    ids = extract_by_paragraph(content_id, min_words, max_snippets, style)
    return json.dumps(ids)


@mcp.tool(
    title="Extract similar sections",
    description="""Extract sections containing a specific keyword or topic with surrounding context.

    Parameters:
    - content_id (str, required): UUID of the source content node to extract from.
    - keyword (str, required): Keyword or phrase to search for. Search is case-insensitive.
    - context_sentences (int, optional): Number of sentences before and after the match to include for context. Defaults to 2.
    - style (list[str], optional): Style tags to apply. Defaults to ["snippet"].

    Returns: JSON array of UUIDs for the newly created snippet nodes, one per keyword occurrence.

    Use cases:
    - Extract all sections discussing a specific topic
    - Create focused snippets around key concepts
    - Build topic-specific collections from broader content

    Note: Each extracted snippet is tagged with the keyword (normalized as slug) in addition to source tags.
    Useful for building thematic collections across multiple source documents.
    """
)
async def tool_extract_similar_sections(
    content_id: str,
    keyword: str,
    context_sentences: int = 2,
    style: Optional[List[str]] = None,
) -> str:
    ids = extract_similar_sections(content_id, keyword, context_sentences, style)
    return json.dumps(ids)


@mcp.tool(
    title="Extract for social media",
    description="""Extract punchy, quotable snippets optimized for social media platforms.

    Parameters:
    - content_id (str, required): UUID of the source content node to extract from.
    - platform (str, optional): Target social platform. Options: "twitter" (280 chars), "linkedin" (700 chars), "instagram" (500 chars). Defaults to "twitter".
    - max_count (int, optional): Maximum number of social snippets to create. Defaults to 5.

    Returns: JSON array of UUIDs for the newly created snippet nodes optimized for social sharing.

    Selection heuristics:
    - Prioritizes sentences with questions or action words (discover, learn, build, create, etc.)
    - Respects platform character limits
    - Filters out fragments and overly short/long sentences
    - Tags snippets with platform name and "social-media"

    Use cases:
    - Auto-generate tweet threads from blog posts
    - Create LinkedIn post variations
    - Extract Instagram captions from long-form content

    Note: Source URLs are automatically copied to social snippets for easy link sharing.
    """
)
async def tool_extract_for_social_media(
    content_id: str,
    platform: str = "twitter",
    max_count: int = 5,
) -> str:
    ids = extract_for_social_media(content_id, platform, max_count)
    return json.dumps(ids)


@mcp.tool(
    title="Combine related snippets",
    description="""Combine multiple snippets or content nodes into a single longer-form piece.

    Parameters:
    - content_ids (list[str], required): List of content node UUIDs to combine, in order.
    - title (str, required): Title for the combined content.
    - style (list[str], optional): Style tags for the combined piece (e.g., ["blog", "post"]). Defaults to ["blog", "post"].
    - separator (str, optional): Text to insert between combined sections. Defaults to "\\n\\n---\\n\\n".

    Returns: UUID of the newly created combined content node.

    Metadata handling:
    - Tags: Union of all tags from source snippets
    - Authors: Union of all authors from source snippets
    - Links: All source snippets get "related_to" relationships with the combined piece

    Use cases:
    - Assemble a blog post from collected snippets
    - Create a comprehensive guide from atomic units
    - Build documentation from scattered notes

    Note: Invalid content IDs are silently skipped. At least one valid ID is required.
    """
)
async def tool_combine_related_snippets(
    content_ids: List[str],
    title: str,
    style: Optional[List[str]] = None,
    separator: str = "\n\n---\n\n",
) -> str:
    return combine_related_snippets(content_ids, title, style, separator)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
