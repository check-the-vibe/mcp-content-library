from __future__ import annotations
import json
import os
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from pathlib import Path
from datetime import datetime, timezone
from schemas import ContentNode, TagNode, StyleNode, AuthorNode, LinkNode, slugify, ensure_style

ROOT = Path(os.environ.get("MCP_SNIPPETS_ROOT", os.path.expanduser("~/.mcp_snippets")))
NODE_DIRS = {
    "content": ROOT / "nodes" / "content",
    "tag": ROOT / "nodes" / "tag",
    "style": ROOT / "nodes" / "style",
    "author": ROOT / "nodes" / "author",
    "link": ROOT / "nodes" / "link",
}
EDGE_DIR = ROOT / "edges"
INDEX_DIR = ROOT / "index"
TMP_DIR = ROOT / "tmp" / "locks"

for p in [*NODE_DIRS.values(), EDGE_DIR, INDEX_DIR, TMP_DIR]:
    p.mkdir(parents=True, exist_ok=True)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, obj: Dict[str, Any]):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _append_jsonl(path: Path, obj: Dict[str, Any]):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def add_content(
    content: str,
    title: Optional[str] = None,
    date: Optional[str] = None,
    style: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    authors: Optional[List[str]] = None,
) -> str:
    cid = str(uuid.uuid4())
    if style:
        style = [ensure_style(s) for s in style]
    node = ContentNode(
        id=cid,
        title=title,
        date=date or _iso_now(),
        style=style or [],
        tags=tags or [],
        authors=authors or [],
        content=content,
    )
    path = NODE_DIRS["content"] / f"{cid}.json"
    _write_json(path, asdict(node))
    for t in node.tags:
        link_tag(cid, t)
    for a in node.authors:
        link_author(cid, a)
    try:
        from search import index_document

        index_document(cid, asdict(node))
    except Exception:
        pass
    return cid


def get_node(node_id: str) -> Dict[str, Any]:
    for base in NODE_DIRS.values():
        p = base / f"{node_id}.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(node_id)


def add_tag(name: str) -> str:
    slug = slugify(name)
    path = NODE_DIRS["tag"] / f"{slug}.json"
    if not path.exists():
        _write_json(path, asdict(TagNode(id=slug, name=name)))
    return slug


def add_style(name: str) -> str:
    ensure_style(name)
    slug = slugify(name)
    path = NODE_DIRS["style"] / f"{slug}.json"
    if not path.exists():
        _write_json(path, asdict(StyleNode(id=slug, name=name)))
    return slug


def add_author(
    name: str,
    linkedin_username: str = "",
    twitter_username: str = "",
    substack_username: str = "",
    reddit_username: str = "",
) -> str:
    slug = slugify(name)
    path = NODE_DIRS["author"] / f"{slug}.json"
    if not path.exists():
        node = AuthorNode(
            id=slug,
            name=name,
            linkedin_username=linkedin_username,
            twitter_username=twitter_username,
            substack_username=substack_username,
            reddit_username=reddit_username,
        )
        _write_json(path, asdict(node))
    return slug


def add_link(url: str, title: Optional[str] = None, description: Optional[str] = None) -> str:
    """
    Create or return a link node by URL.
    Uses URL as the unique identifier (slugified).
    """
    slug = slugify(url)
    path = NODE_DIRS["link"] / f"{slug}.json"
    if not path.exists():
        node = LinkNode(
            id=slug,
            url=url,
            title=title,
            description=description,
        )
        _write_json(path, asdict(node))
    return slug


def link_relates(src_content_id: str, relation_type: str, dst_content_id: str):
    assert relation_type in {"snippet_of", "related_to"}
    _append_jsonl(
        EDGE_DIR / "relates.jsonl",
        {
            "src": src_content_id,
            "type": relation_type,
            "dst": dst_content_id,
            "date": _iso_now(),
        },
    )


def link_tag(content_id: str, tag_name_or_slug: str):
    slug = slugify(tag_name_or_slug)
    add_tag(slug)
    _append_jsonl(
        EDGE_DIR / "tags.jsonl",
        {
            "content": content_id,
            "type": "is_tagged",
            "tag": slug,
            "date": _iso_now(),
        },
    )


def link_author(content_id: str, author_name_or_slug: str):
    slug = slugify(author_name_or_slug)
    add_author(slug)
    _append_jsonl(
        EDGE_DIR / "authors.jsonl",
        {
            "content": content_id,
            "type": "authored",
            "author": slug,
            "date": _iso_now(),
        },
    )


def link_url(content_id: str, url: str, title: Optional[str] = None, description: Optional[str] = None):
    """
    Link a content node to a URL by creating/fetching a link node
    and establishing a has_link edge.
    """
    link_slug = add_link(url, title, description)
    _append_jsonl(
        EDGE_DIR / "links.jsonl",
        {
            "content": content_id,
            "type": "has_link",
            "link": link_slug,
            "date": _iso_now(),
        },
    )

def get_content_links(content_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all link nodes associated with a content node.
    Returns a list of link node dictionaries with their full data.
    """
    links_path = EDGE_DIR / "links.jsonl"
    link_nodes = []
    if links_path.exists():
        for line in links_path.read_text(encoding="utf-8").splitlines():
            try:
                edge = json.loads(line)
                if edge.get("content") == content_id:
                    link_slug = edge.get("link")
                    link_path = NODE_DIRS["link"] / f"{link_slug}.json"
                    if link_path.exists():
                        link_nodes.append(json.loads(link_path.read_text(encoding="utf-8")))
            except Exception:
                continue
    return link_nodes


def get_all_content_count() -> int:
    """
    Get the total count of stored content items.
    """
    try:
        return len(list(NODE_DIRS["content"].glob("*.json")))
    except Exception:
        return 0


def iter_content_nodes():
    for p in NODE_DIRS["content"].glob("*.json"):
        try:
            yield json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
