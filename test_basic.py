#!/usr/bin/env python
"""Basic end-to-end test of MCP Content Library functionality."""

import json
import sys
from storage import (
    add_content,
    add_tag,
    add_author,
    add_link,
    link_url,
    link_tag,
    get_node,
    get_content_links,
)
from search import search, rebuild_index
from content_tools import extract_by_paragraph, extract_for_social_media
from schemas import slugify


def test_basic_workflow():
    """Test a complete workflow: create content, add metadata, search, extract."""
    print("=== MCP Content Library - Basic Test ===\n")

    # Test 1: Tag normalization
    print("1. Testing tag normalization...")
    tag1 = slugify("Machine Learning!")
    tag2 = slugify("AI & ML")
    assert tag1 == "machine-learning", f"Expected 'machine-learning', got '{tag1}'"
    assert tag2 == "ai-ml", f"Expected 'ai-ml', got '{tag2}'"
    print(f"   ✓ Tags normalized: '{tag1}', '{tag2}'")

    # Test 2: Create author
    print("\n2. Creating author...")
    author_id = add_author(
        "Jane Doe",
        twitter_username="janedoe",
        linkedin_username="janedoe",
    )
    assert author_id == "jane-doe"
    print(f"   ✓ Author created: {author_id}")

    # Test 3: Create content with metadata
    print("\n3. Creating content...")
    content_text = """Machine learning is transforming software development.

    It enables systems to learn from data and improve over time.

    The best products solve real problems. Focus on user needs first.

    How do we build better AI systems? Start with solid foundations."""

    content_id = add_content(
        content=content_text,
        title="AI Development Philosophy",
        style=["blog", "post"],
        tags=["machine-learning", "ai", "product-management"],
        authors=["jane-doe"],
    )
    print(f"   ✓ Content created: {content_id}")

    # Test 4: Add and link URL
    print("\n4. Linking source URL...")
    link_url(
        content_id,
        "https://blog.example.com/ai-philosophy",
        title="Original Blog Post",
    )
    print(f"   ✓ URL linked")

    # Test 5: Retrieve content with links
    print("\n5. Retrieving content...")
    node = get_node(content_id)
    assert node["type"] == "content"
    assert node["title"] == "AI Development Philosophy"
    links = get_content_links(content_id)
    assert len(links) > 0
    print(f"   ✓ Content retrieved with {len(links)} link(s)")

    # Test 6: Search
    print("\n6. Testing search...")
    rebuild_index()
    results = search(
        query="machine learning",
        filters={"tag": ["ai"]},
        sort="relevance",
        page=1,
        page_size=10,
    )
    assert results["total"] >= 1
    print(f"   ✓ Search found {results['total']} result(s)")

    # Test 7: Extract by paragraph
    print("\n7. Extracting paragraphs...")
    snippet_ids = extract_by_paragraph(
        content_id, min_words=5, max_snippets=3, style=["snippet"]
    )
    assert len(snippet_ids) > 0
    print(f"   ✓ Extracted {len(snippet_ids)} paragraph snippet(s)")

    # Test 8: Extract social media snippets
    print("\n8. Extracting social media snippets...")
    social_ids = extract_for_social_media(
        content_id, platform="twitter", max_count=2
    )
    print(f"   ✓ Extracted {len(social_ids)} social snippet(s)")

    # Test 9: Verify snippet relationships
    if snippet_ids:
        print("\n9. Verifying snippet metadata...")
        snippet = get_node(snippet_ids[0])
        assert snippet["type"] == "content"
        assert "snippet" in snippet.get("style", [])
        print(f"   ✓ Snippet has correct style tags")

    print("\n=== All Tests Passed! ===")
    return True


if __name__ == "__main__":
    try:
        test_basic_workflow()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
