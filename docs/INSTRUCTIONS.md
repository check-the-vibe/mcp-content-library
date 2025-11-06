I would like to use the modelcontextprotocol python sdk to accomplish the following task. We will be running this code in a linux environment, assume we have python3 and pip, use a local, file system-based approach for storing the relevant information that is described. DO not use any databases or other 3rd party storage systems, only the file system, a structured file-based layer for structured data retrieval/storage, and raw python. Define the architecture plan and the steps needed to get to a working POC. 

Create an MCP interface that acts as a snippet and projects manager. This should include the structure of different types of content. There should be a graph relationship between longer pieces of content, and their constituent / related snippets. 

The purpose of this MCP writing tool is to build _instant context_ for an LLM to use when generating creating writing content. This allows a user to adapt the default output of an LLM to a specific style or tone of voice. This can happen in a number of different methods, which include ‘randomizing’ a tone of voice based on the returned output, adapting/aligning to a set of content’s tone, building combined content from a set of snippets into a longer form piece, extracting a longer form piece into constituent sets of snippets/content types. 

Each content ‘node’ should include: 
- content
- title?
- date
- style[]
- relates[]
- tags[]
- authors[]
Each tag ‘node’ should include: 
- name
Each style ‘node’ should include: 
- name
	- Enumerated list: chapter, blog, post, snippet, tweet
Each author ‘node’ should contain:
- name
- linkedin_username
- twitter_username
- substack_username
- reddit_username
The relates[] edges come in the form of:
- snippet_of
- related_to
The tags[] edges come in the form of: 
- is_tagged
The authors[] edges come in the form of: 
- authored
The MCP interface should allow a user to perform a number of searches, which essentially add/remove ‘filter’s on content: 
- tag
- title
- content
- author
- relates
- style
For ‘edge searches’ (tag, author, relates), the search will perform first a lookup of the node in question (tag/author/content/style), and then perform a search and filtering based on the relationships to the (set of) node responses. If a filter is not explicitly called out, then assume ‘all’. 
Results can be sorted when returned, in a paginated list: 
- date
- ‘relevance’
- random


--———————————————————————————————————


  

MCP Snippets & Projects Manager — Architecture + POC (filesystem-only)

  

  

This plan and reference implementation show how to build a Model Context Protocol (MCP) server (Python SDK) that manages a local knowledge base of writing assets: long-form pieces and their constituent snippets, plus tags, styles, authors, and graph relationships between nodes. The goal is instant context for LLM-driven creative writing.

  

  

  

  

1) High-level architecture

  

  

Constraints

  

- Linux environment, Python 3, pip
- No databases or third‑party storage — filesystem only
- A thin, structured file-based layer for storage/retrieval
- Raw Python (no heavy frameworks)
- Expose functionality via an MCP server (Python SDK mcp), tools-first API

  

  

Overview

  

- MCP Server exposes tools for CRUD, linking, search, and curation.
- Storage Layer writes canonical JSON nodes and JSONL edges to a project root.
- Indexes (optional but recommended): maintain a simple inverted index + metadata caches for relevance, pagination and filters.
- Search Engine (lightweight): tokenization, TF‑IDF-ish scoring, plus filters (author/tag/style/relates/title/content). Sort by date, relevance, or random.
- Graph Model: content nodes connect to other content (e.g., snippet_of, related_to) and to tag/style/author via edges. This supports bottom‑up (snippets → long piece) and top‑down (long piece → snippets) workflows.

  

  

Directory Layout (everything under a configurable ROOT, e.g., ~/.mcp_snippets):

ROOT/

  nodes/

    content/{uuid}.json

    tag/{slug}.json

    style/{slug}.json

    author/{slug}.json

  edges/

    relates.jsonl           # content<->content edges (types: snippet_of, related_to)

    tags.jsonl              # content<->tag edges   (type: is_tagged)

    authors.jsonl           # content<->author edges(type: authored)

  index/

    inverted.json           # { token: { content_id: tf, ... }, ... }

    doclens.json            # { content_id: length } for normalization

    meta.json               # { content_id: {date, title, style[], ...} } cache

  manifests/

    integrity.json          # counts, last_reindex time, etc.

  tmp/

    locks/

Why JSON + JSONL?

  

- Human‑readable, easy diffs
- Append‑only logs for edges (JSONL) simplify writes
- Node files are the source of truth; indexes are derivative and can be rebuilt

  

  

  

  

  

2) Data model

  

  

  

2.1 Node Schemas (JSON)

  

  

Content Node (nodes/content/{uuid}.json):

{

  "id": "uuid4",

  "type": "content",

  "title": "optional title",

  "date": "2025-11-05T12:34:56Z",

  "style": ["chapter"],

  "tags": ["sci-fi", "noir"],

  "authors": ["jane_doe"],

  "relates": [],

  "content": "Full text…"

}

Tag Node (nodes/tag/{slug}.json):

{"id": "slug", "type": "tag", "name": "noir"}

Style Node (nodes/style/{slug}.json):

{"id": "slug", "type": "style", "name": "chapter"}

Enumerated style names: chapter, blog, post, snippet, tweet.

  

Author Node (nodes/author/{slug}.json):

{

  "id": "slug",

  "type": "author",

  "name": "Jane Doe",

  "linkedin_username": "janedoe",

  "twitter_username": "janedoe",

  "substack_username": "janedoe",

  "reddit_username": "janedoe"

}

  

2.2 Edge Schemas (JSONL)

  

  

relates.jsonl (content↔content):

{"src": "content_uuid_A", "type": "snippet_of", "dst": "content_uuid_B", "date": "2025-11-05T12:00:00Z"}

{"src": "content_uuid_A", "type": "related_to", "dst": "content_uuid_C", "date": "2025-11-05T12:00:05Z"}

tags.jsonl (content↔tag):

{"content": "content_uuid_A", "type": "is_tagged", "tag": "noir"}

authors.jsonl (content↔author):

{"content": "content_uuid_A", "type": "authored", "author": "jane_doe"}

All writes include an ISO8601 date. All IDs/refs are strings. Content nodes are the only ones with content text.

  

  

  

  

3) Core operations exposed via MCP tools

  

  

- Node CRUD  
    

- add_content(content, title?, date?, style[], tags[], authors[]) -> id
- add_tag(name) -> id
- add_style(name) -> id (validated against enum)
- add_author(name, linkedin_username?, twitter_username?, substack_username?, reddit_username?) -> id
- get_node(id or slug) / update_content(id, ...) / delete_node(id) (soft delete optional)

-   
    
- Edges  
    

- link_relates(src_content_id, relation_type, dst_content_id) where relation_type ∈ {snippet_of, related_to}
- link_tag(content_id, tag_slug) (creates tag if missing)
- link_author(content_id, author_slug) (creates author if missing)

-   
    
- Search & Filters  
    

- search_content(query?, filters?, sort?, page?, page_size?, seed?) -> {items, total, page, page_size}  
    

- filters keys (all optional; default = all): tag[], title, content, author[], relates[] (ids or relation descriptors), style[]
- edge-first lookups: resolve tag/author/style/content ids, then filter via edges
- sort: date (desc), relevance (TF‑IDF-ish), random (stable if seed provided)

-   
    

-   
    
- Curation helpers (for “instant context”)  
    

- assemble_longform_from_snippets(parent_id or tag/style query set) -> merged_content
- extract_snippets_from_content(content_id, strategy?) -> [snippet_ids]
- tone_randomize(content_id or text, seed?) -> text
- tone_adapt(text or content_id, reference_ids[]) -> text

-   
    

  

  

POC exposes the first three groups; curation helpers can be stubs initially (pure functions inside the server) and refined later.

  

  

  

  

4) Lightweight indexing & relevance

  

  

- Tokenizer: lowercased, Unicode letters+digits, stopword list, simple stemming optional (e.g., suffix drops ing, ed, s).
- Inverted index: index/inverted.json → { token: { doc_id: tf } }.
- Doc lengths: index/doclens.json → { doc_id: length }.
- Meta cache: index/meta.json → { doc_id: {...fields needed for filters/sort} }.
- Reindexing: upon writes, update affected doc only; rebuild_index() utility to rescan if needed.
- Scoring: score(q,d) = Σ (tf_d,t * idf_t) / sqrt(doc_len_d) with idf_t = log((1+N)/(1+df_t)) + 1.

  

  

  

  

  

5) Concurrency & integrity

  

  

- Use file‑based advisory locks per index file (tmp/locks/index.lock) during writes.
- Append‑only for *.jsonl; compact on reindex.
- Validate schemas pre‑write; keep backups (.bak) on update.

  

  

  

  

  

6) Step-by-step to a working POC

  

  

7. Bootstrap project

  

python -m venv .venv && source .venv/bin/activate

pip install "mcp[cli]" starlette uvicorn

mkdir -p ~/.mcp_snippets

  

2. Create the server module (server.py) and storage/search utils (storage.py, search.py, schemas.py).
3. Run locally

  

python server.py   # stdio transport (for MCP hosts)

  

4. (Optional) Test via MCP CLI

  

mcp dev server.py  # if available in your environment

  

5. Seed sample data: add a few authors/tags/styles, add 2 long pieces + ~6 snippets with snippet_of edges.
6. Try searches

  

  

  

- Filter by tag=noir, sort by relevance
- Filter by author=jane_doe, sort by date
- Filter by relates=parent_longform_id, sort by random

  

  

  

7. Iterate: expand curation helpers (tone adapt, snippet extraction, assembly).

  

  

  

  

  

8) MCP server — reference implementation (filesystem only)

  

  

Drop these files next to each other. Adjust ROOT as needed. The code avoids third‑party storage; only uses Python stdlib + mcp.

  

  

schemas.py

  

from __future__ import annotations

from dataclasses import dataclass, asdict, field

from typing import List, Dict, Any, Optional

import re

  

STYLE_ENUM = {"chapter", "blog", "post", "snippet", "tweet"}

  

@dataclass

class ContentNode:

    id: str

    type: str = "content"

    title: Optional[str] = None

    date: str = ""

    style: List[str] = field(default_factory=list)

    tags: List[str] = field(default_factory=list)

    authors: List[str] = field(default_factory=list)

    relates: List[str] = field(default_factory=list)  # optional denormalized hints

    content: str = ""

  

@dataclass

class TagNode:

    id: str

    type: str = "tag"

    name: str = ""

  

@dataclass

class StyleNode:

    id: str

    type: str = "style"

    name: str = ""

  

@dataclass

class AuthorNode:

    id: str

    type: str = "author"

    name: str = ""

    linkedin_username: str = ""

    twitter_username: str = ""

    substack_username: str = ""

    reddit_username: str = ""

  

# Basic validators

  

def slugify(s: str) -> str:

    s = s.strip().lower()

    s = re.sub(r"[^a-z0-9_\-]+", "-", s)

    s = re.sub(r"-+", "-", s)

    return s.strip("-")

  

def ensure_style(name: str) -> str:

    if name not in STYLE_ENUM:

        raise ValueError(f"Invalid style '{name}'. Allowed: {sorted(STYLE_ENUM)}")

    return name

  

storage.py

  

from __future__ import annotations

import json, os, uuid, time, io, random, math, re, contextlib

from typing import Dict, Any, List, Optional

from dataclasses import asdict

from pathlib import Path

from datetime import datetime, timezone

from schemas import ContentNode, TagNode, StyleNode, AuthorNode, slugify, ensure_style

  

ROOT = Path(os.environ.get("MCP_SNIPPETS_ROOT", os.path.expanduser("~/.mcp_snippets")))

NODE_DIRS = {"content": ROOT/"nodes"/"content", "tag": ROOT/"nodes"/"tag", "style": ROOT/"nodes"/"style", "author": ROOT/"nodes"/"author"}

EDGE_DIR = ROOT/"edges"

INDEX_DIR = ROOT/"index"

TMP_DIR = ROOT/"tmp"/"locks"

  

for p in [*NODE_DIRS.values(), EDGE_DIR, INDEX_DIR, TMP_DIR]:

    p.mkdir(parents=True, exist_ok=True)

  

# ---- File helpers ----

  

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

  

# ---- Node CRUD ----

  

def add_content(content: str, title: Optional[str]=None, date: Optional[str]=None, style: Optional[List[str]]=None, tags: Optional[List[str]]=None, authors: Optional[List[str]]=None) -> str:

    cid = str(uuid.uuid4())

    if style:

        style = [ensure_style(s) for s in style]

    node = ContentNode(id=cid, title=title, date=date or _iso_now(), style=style or [], tags=tags or [], authors=authors or [], content=content)

    path = NODE_DIRS["content"]/f"{cid}.json"

    _write_json(path, asdict(node))

    # link edges for tags/authors

    for t in node.tags:

        link_tag(cid, slugify(t))

    for a in node.authors:

        link_author(cid, slugify(a))

    # index

    from search import index_document

    index_document(cid, node)

    return cid

  

def get_node(node_id: str) -> Dict[str, Any]:

    # try content, tag, style, author

    for kind, base in NODE_DIRS.items():

        p = base / f"{node_id}.json"

        if p.exists():

            return json.loads(p.read_text(encoding="utf-8"))

    # also try slugs for tag/style/author

    for kind in ("tag","style","author"):

        p = NODE_DIRS[kind]/f"{node_id}.json"

        if p.exists():

            return json.loads(p.read_text(encoding="utf-8"))

    raise FileNotFoundError(node_id)

  

# Tag/style/author ensure + add

  

def add_tag(name: str) -> str:

    slug = slugify(name)

    path = NODE_DIRS["tag"]/f"{slug}.json"

    if not path.exists():

        _write_json(path, asdict(TagNode(id=slug, name=name)))

    return slug

  

def add_style(name: str) -> str:

    ensure_style(name)

    slug = slugify(name)

    path = NODE_DIRS["style"]/f"{slug}.json"

    if not path.exists():

        _write_json(path, asdict(StyleNode(id=slug, name=name)))

    return slug

  

def add_author(name: str, linkedin_username: str="", twitter_username: str="", substack_username: str="", reddit_username: str="") -> str:

    slug = slugify(name)

    path = NODE_DIRS["author"]/f"{slug}.json"

    if not path.exists():

        node = AuthorNode(id=slug, name=name, linkedin_username=linkedin_username, twitter_username=twitter_username, substack_username=substack_username, reddit_username=reddit_username)

        _write_json(path, asdict(node))

    return slug

  

# ---- Edges ----

  

def link_relates(src_content_id: str, relation_type: str, dst_content_id: str):

    assert relation_type in {"snippet_of","related_to"}

    EDGE_DIR.mkdir(parents=True, exist_ok=True)

    _append_jsonl(EDGE_DIR/"relates.jsonl", {"src": src_content_id, "type": relation_type, "dst": dst_content_id, "date": _iso_now()})

  

  

def link_tag(content_id: str, tag_slug: str):

    add_tag(tag_slug)

    _append_jsonl(EDGE_DIR/"tags.jsonl", {"content": content_id, "type": "is_tagged", "tag": tag_slug, "date": _iso_now()})

  

  

def link_author(content_id: str, author_slug: str):

    add_author(author_slug)

    _append_jsonl(EDGE_DIR/"authors.jsonl", {"content": content_id, "type": "authored", "author": author_slug, "date": _iso_now()})

  

# ---- Utilities for scans (used by search) ----

  

def iter_content_nodes():

    for p in NODE_DIRS["content"].glob("*.json"):

        try:

            yield json.loads(p.read_text(encoding="utf-8"))

        except Exception:

            continue

  

search.py

  

from __future__ import annotations

import json, os, math, random, re

from collections import defaultdict

from typing import Dict, Any, List, Optional, Tuple

from pathlib import Path

from schemas import STYLE_ENUM

from storage import INDEX_DIR, NODE_DIRS

  

TOKEN_RE = re.compile(r"[\p{L}\p{N}]+", re.UNICODE)

STOP = {"the","and","a","to","of","in","it","is","that","on","for","as","with","this","be"}

  

def _tokenize(text: str) -> List[str]:

    if not text:

        return []

    text = text.lower()

    tokens = re.findall(r"[a-z0-9]+", text)

    return [t for t in tokens if t not in STOP]

  

# ---- Index files ----

INV_PATH = INDEX_DIR/"inverted.json"

LEN_PATH = INDEX_DIR/"doclens.json"

META_PATH = INDEX_DIR/"meta.json"

  

# ---- Indexing ----

  

def index_document(doc_id: str, node: Dict[str, Any]):

    inv = json.loads(INV_PATH.read_text()) if INV_PATH.exists() else {}

    lens = json.loads(LEN_PATH.read_text()) if LEN_PATH.exists() else {}

    meta = json.loads(META_PATH.read_text()) if META_PATH.exists() else {}

  

    text = (node.get("title") or "") + "\n" + (node.get("content") or "")

    toks = _tokenize(text)

    tf: Dict[str,int] = defaultdict(int)

    for t in toks:

        tf[t]+=1

    for t,cnt in tf.items():

        inv.setdefault(t, {})[doc_id] = cnt

    lens[doc_id] = len(toks) or 1

    meta[doc_id] = {

        "date": node.get("date",""),

        "title": node.get("title"),

        "style": node.get("style",[]),

        "tags": node.get("tags",[]),

        "authors": node.get("authors",[])

    }

    INV_PATH.write_text(json.dumps(inv))

    LEN_PATH.write_text(json.dumps(lens))

    META_PATH.write_text(json.dumps(meta))

  

  

def rebuild_index():

    inv, lens, meta = {}, {}, {}

    for p in NODE_DIRS["content"].glob("*.json"):

        node = json.loads(p.read_text())

        doc_id = node["id"]

        text = (node.get("title") or "") + "\n" + (node.get("content") or "")

        toks = _tokenize(text)

        tf: Dict[str,int] = defaultdict(int)

        for t in toks:

            tf[t]+=1

        for t,cnt in tf.items():

            inv.setdefault(t, {})[doc_id] = cnt

        lens[doc_id] = len(toks) or 1

        meta[doc_id] = {

            "date": node.get("date",""),

            "title": node.get("title"),

            "style": node.get("style",[]),

            "tags": node.get("tags",[]),

            "authors": node.get("authors",[])

        }

    INV_PATH.write_text(json.dumps(inv))

    LEN_PATH.write_text(json.dumps(lens))

    META_PATH.write_text(json.dumps(meta))

  

# ---- Search ----

  

def _idf(inv: Dict[str, Dict[str,int]], t: str) -> float:

    N = max(1, len({d for postings in inv.values() for d in postings}))

    df = len(inv.get(t, {}))

    return math.log((1+N)/(1+df)) + 1.0

  

  

def _score(inv, lens, q_toks) -> Dict[str, float]:

    scores = defaultdict(float)

    idf_cache = {t: _idf(inv,t) for t in set(q_toks)}

    for t in q_toks:

        postings = inv.get(t, {})

        for doc, tf in postings.items():

            scores[doc] += (tf * idf_cache[t]) / math.sqrt(lens.get(doc,1))

    return scores

  

  

def _load_indexes():

    inv = json.loads(INV_PATH.read_text()) if INV_PATH.exists() else {}

    lens = json.loads(LEN_PATH.read_text()) if LEN_PATH.exists() else {}

    meta = json.loads(META_PATH.read_text()) if META_PATH.exists() else {}

    return inv, lens, meta

  

  

def search(query: Optional[str], filters: Dict[str, Any], sort: str="relevance", page: int=1, page_size: int=10, seed: Optional[int]=None) -> Dict[str, Any]:

    inv, lens, meta = _load_indexes()

    q_toks = _tokenize(query or "")

  

    # start set = all docs

    docset = set(meta.keys())

  

    # edge-style filters use cached meta for tags/authors/style; relates handled by scanning edges lazily

    if filters.get("style"):

        styles = [s for s in filters["style"] if s in STYLE_ENUM]

        docset &= {d for d,m in meta.items() if any(s in m.get("style",[]) for s in styles)}

  

    if filters.get("tag"):

        tags = set(filters["tag"])

        docset &= {d for d,m in meta.items() if any(t in m.get("tags",[]) for t in tags)}

  

    if filters.get("author"):

        authors = set(filters["author"])

        docset &= {d for d,m in meta.items() if any(a in m.get("authors",[]) for a in authors)}

  

    # title/content literal filters

    if filters.get("title"):

        substr = filters["title"].lower()

        docset &= {d for d,m in meta.items() if (m.get("title") or "").lower().find(substr) >= 0}

    if filters.get("content"):

        # literal content scan fallback (could be optimized)

        from pathlib import Path

        content_dir = NODE_DIRS["content"]

        substr = filters["content"].lower()

        keep = set()

        for d in list(docset):

            p = content_dir / f"{d}.json"

            if p.exists():

                txt = json.loads(p.read_text()).get("content",""")".lower()

                if substr in txt:

                    keep.add(d)

        docset &= keep

  

    # relates: set of content ids; include where edges mention these ids

    if filters.get("relates"):

        rels = set(filters["relates"])

        import json, pathlib

        keep = set()

        rel_path = pathlib.Path(NODE_DIRS["content"]).parent.parent/"edges"/"relates.jsonl"

        if rel_path.exists():

            for line in rel_path.read_text().splitlines():

                try:

                    obj = json.loads(line)

                    if obj.get("src") in docset or obj.get("dst") in docset:

                        if obj.get("src") in rels or obj.get("dst") in rels:

                            keep.add(obj.get("src"))

                            keep.add(obj.get("dst"))

                except Exception:

                    continue

        docset &= keep

  

    candidates = list(docset)

  

    # scoring

    if sort == "relevance":

        scores = _score(inv, lens, q_toks) if q_toks else {d:0.0 for d in candidates}

        candidates.sort(key=lambda d: scores.get(d, 0.0), reverse=True)

    elif sort == "date":

        candidates.sort(key=lambda d: (meta.get(d,{}).get("date") or ""), reverse=True)

    elif sort == "random":

        rnd = random.Random(seed)

        rnd.shuffle(candidates)

  

    total = len(candidates)

    start = max(0, (page-1)*page_size)

    end = start + page_size

    page_items = candidates[start:end]

  

    # hydrate

    out = []

    for d in page_items:

        p = NODE_DIRS["content"]/f"{d}.json"

        if p.exists():

            out.append(json.loads(p.read_text()))

    return {"items": out, "total": total, "page": page, "page_size": page_size}

  

server.py

 (MCP server)

  

from __future__ import annotations

import json

from typing import Any, Optional, List, Dict

from mcp.server.fastmcp import FastMCP

from storage import add_content, add_tag, add_style, add_author, link_relates, link_tag, link_author, get_node

from search import search, rebuild_index

  

mcp = FastMCP("snippets_manager")

  

@mcp.tool()

async def tool_add_content(content: str, title: Optional[str]=None, date: Optional[str]=None, style: Optional[List[str]]=None, tags: Optional[List[str]]=None, authors: Optional[List[str]]=None) -> str:

    """Create a content node. Returns the new content id.

    Args:

      content: Full text body

      title: Optional title

      date: ISO8601. Defaults to now (UTC)

      style: List of style names (chapter, blog, post, snippet, tweet)

      tags: List of tag slugs or names

      authors: List of author slugs or names

    """

    return add_content(content, title, date, style, tags, authors)

  

@mcp.tool()

async def tool_add_tag(name: str) -> str:

    """Create or ensure a tag node by name/slug."""

    return add_tag(name)

  

@mcp.tool()

async def tool_add_style(name: str) -> str:

    """Create or ensure a style node. Must be one of: chapter, blog, post, snippet, tweet."""

    return add_style(name)

  

@mcp.tool()

async def tool_add_author(name: str, linkedin_username: str="", twitter_username: str="", substack_username: str="", reddit_username: str="") -> str:

    """Create or ensure an author node; returns the author slug."""

    return add_author(name, linkedin_username, twitter_username, substack_username, reddit_username)

  

@mcp.tool()

async def tool_link_relates(src_content_id: str, relation_type: str, dst_content_id: str) -> str:

    """Create a content↔content edge. relation_type ∈ {snippet_of, related_to}."""

    link_relates(src_content_id, relation_type, dst_content_id)

    return "ok"

  

@mcp.tool()

async def tool_link_tag(content_id: str, tag_slug: str) -> str:

    """Link a content node to a tag (creates tag if needed)."""

    link_tag(content_id, tag_slug)

    return "ok"

  

@mcp.tool()

async def tool_link_author(content_id: str, author_slug: str) -> str:

    """Link a content node to an author (creates author if needed)."""

    link_author(content_id, author_slug)

    return "ok"

  

@mcp.tool()

async def tool_search(query: Optional[str]=None, filters_json: Optional[str]=None, sort: str="relevance", page: int=1, page_size: int=10, seed: Optional[int]=None) -> str:

    """Search content with filters and sort.

    Args:

      query: free text query

      filters_json: JSON dict with optional keys: tag[list], title[str], content[str], author[list], relates[list], style[list]

      sort: one of relevance, date, random

      page: 1-based page index

      page_size: results per page

      seed: optional int to stabilize `random` sort

    Returns JSON string {items,total,page,page_size}.

    """

    filters = json.loads(filters_json) if filters_json else {}

    res = search(query, filters, sort=sort, page=page, page_size=page_size, seed=seed)

    return json.dumps(res)

  

@mcp.tool()

async def tool_get_node(node_id: str) -> str:

    """Fetch any node by id/slug as JSON string."""

    return json.dumps(get_node(node_id))

  

@mcp.tool()

async def tool_reindex() -> str:

    """Rebuild the inverted index and metadata cache from scratch."""

    rebuild_index()

    return "ok"

  

# Entry point

  

def main():

    mcp.run(transport='stdio')

  

if __name__ == "__main__":

    main()

  

  

  

  

8) Example flows (what the POC already enables)

  

  

  

Add a long piece, then connect snippets

  

  

1. tool_add_author(name="Jane Doe") → "jane-doe"
2. tool_add_tag(name="noir") → "noir"
3. tool_add_style(name="chapter")
4. tool_add_content(title="Night Market", style=["chapter"], authors=["jane-doe"], tags=["noir"], content="…long text…") → parent_id
5. For each snippet: tool_add_content(style=["snippet"], authors=["jane-doe"], tags=["noir"], content="…snippet…") → child_id
6. Link: tool_link_relates(src_content_id=child_id, relation_type="snippet_of", dst_content_id=parent_id)

  

  

  

Search for snippets of a given parent, sorted by random (stable)

  

  

- tool_search(query=None, filters_json='{"relates": ["<parent_id>", "<child_id>"]}', sort="random", seed=42, page=1, page_size=10)

  

  

  

Search by tag + author, sorted by date

  

  

- tool_search(query="market night", filters_json='{"tag":["noir"], "author":["jane-doe"]}', sort="date")

  

  

  

  

  

9) Extending toward the “instant context” helpers

  

  

- tone_randomize(text, seed): sample synonyms, reorder clauses, vary sentence length; keep POS constraints. Pure function; expose as tool_tone_randomize.
- tone_adapt(text, reference_ids[]): build style vectors from references (avg n‑gram distributions, sentence length, punctuation rate); apply edits to input text.
- assemble_longform_from_snippets(parent_id or filter set): gather snippets via snippet_of edges, order by date/relevance/random; stitch with separators.
- extract_snippets_from_content(content_id, strategy): heuristics (paragraphs, dialogue lines, scene breaks) → new snippet nodes + snippet_of links.

  

  

All of these can be filesystem‑based: outputs are either new content nodes or returned strings.

  

  

  

  

10) Operational notes & guardrails

  

  

- Logging: never write to stdout in MCP servers; log to stderr or files.
- Validation: style enum enforced; reject unknown relation types; sanitize slugs.
- Backups: before overwriting a node, write *.bak.
- Rebuild: tool_reindex if indexes drift; they’re derived from node truth.
- Performance: POC works up to low tens of thousands of docs. For larger sets, shard indexes per token prefix and stream JSONL scans.

  

  

  

  

  

11) What’s included vs. future work

  

  

Included in POC

  

- Filesystem-only storage layer
- Node + edge schemas
- MCP tools for add/link/search
- Lightweight inverted index with TF‑IDF-ish ranking
- Sorting (date, relevance, random) + pagination

  

  

Next steps

  

- Richer edge queries (directional, distance)
- Snippet extraction/assembly + tone helpers
- Resource endpoints to expose canonical resources (e.g., serve compiled longform as a resource: in MCP)
- Export/import bundles (zip the ROOT tree)
- Tests & linting

  

  

  

  

  

12) HTTP transport (Streamable HTTP) — recommended for chat interfaces

  

  

The official Python SDK supports Streamable HTTP (superseding SSE for production) and provides helpers to run or mount your server in an ASGI app. Many popular clients (Claude Desktop, Cursor, Copilot, custom web UIs) can connect to a Streamable HTTP endpoint.

  

  

12.1 Quick switch: run FastMCP over HTTP

  

  

Create server_http.py (or modify server.py entrypoint):

# server_http.py

from server import mcp  # reuse the FastMCP instance you already defined

  

if __name__ == "__main__":

    # Stateful HTTP server with streaming

    mcp.run(transport="streamable-http")

Run it:

python server_http.py  # starts an HTTP server on 127.0.0.1:8000 by default

The endpoint is exposed at http://127.0.0.1:8000/mcp.

  

For a stateless deployment (scales easily, no session persistence), use:

mcp.run(transport="streamable-http", stateless_http=True)

  

12.2 Mount inside a Starlette/ASGI app

  

  

This makes it easy to add CORS, auth, and reverse-proxying.

# app.py

from starlette.applications import Starlette

from starlette.middleware.cors import CORSMiddleware

from starlette.routing import Mount

from server import mcp  # your existing FastMCP instance

  

app = Starlette()

# Mount MCP at /mcp (its default path)

app.router.routes.append(Mount("/", app=mcp.streamable_http_app()))

  

# CORS so browser-based clients can read the session header

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],                # scope this in prod

    allow_methods=["GET","POST","DELETE"],

    allow_headers=["*"],

    expose_headers=["Mcp-Session-Id"],  # required for browser clients

)

Run with uvicorn:

uvicorn app:app --host 0.0.0.0 --port 8000

Clients connect to http://HOST:8000/mcp.

  

  

12.3 SSE (legacy) vs Streamable HTTP

  

  

- Streamable HTTP = default recommendation; supports JSON responses and streaming via SSE under the hood.
- SSE-only servers remain possible (mcp.sse_app()), but the SDK docs indicate Streamable HTTP is the forward path.

  

  

  

12.4 Popular client wiring tips

  

  

- Claude Desktop / Cursor: add a remote MCP server pointing to the Streamable HTTP URL.
- Browser-based UIs: ensure CORS exposes Mcp-Session-Id and that GET/POST/DELETE are allowed.
- Behind a proxy (nginx, Caddy, Cloudflare): enable request buffering off for streaming endpoints and allow text/event-stream if streaming is used.

  

  

  

12.5 Security & deployment knobs

  

  

- Put your ASGI app behind TLS (reverse proxy or --ssl- flags if terminating at app).
- Optionally set an auth middleware (API key/bearer token) at the ASGI layer; MCP itself is transport-agnostic.
- Scale by running multiple uvicorn workers or container replicas; Streamable HTTP is multi-client.

  

  

  

12.6 Minimal client sanity check (Python)

  

import asyncio

from mcp import ClientSession

from mcp.client.streamable_http import streamablehttp_client

  

async def main():

    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (r,w,_):

        async with ClientSession(r,w) as session:

            await session.initialize()

            tools = await session.list_tools()

            print([t.name for t in tools.tools])

  

asyncio.run(main())

  

  

  

  

13) Updated setup steps (including HTTP)

  

  

14. Bootstrap project

  

python -m venv .venv && source .venv/bin/activate

pip install "mcp[cli]" starlette uvicorn

mkdir -p ~/.mcp_snippets

  

2. Keep files from sections 7 (schemas.py, storage.py, search.py, server.py). Add server_http.py or app.py from 12.1/12.2.
3. Run via HTTP (simple)

  

python server_http.py

# connects at http://127.0.0.1:8000/mcp

  

4. Run via ASGI (recommended for chat interfaces)

  

uvicorn app:app --host 0.0.0.0 --port 8000

  

5. Wire a client (Claude Desktop/Cursor/custom) to the Streamable HTTP URL.
6. Proceed with the earlier seed & search workflow; functionality is identical over HTTP.   