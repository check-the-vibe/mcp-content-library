# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MCP Content Library is a Model Context Protocol (MCP) server that provides a graph-based content management system for writing. It stores content nodes (snippets, blog posts, tweets) with rich metadata (tags, authors, styles, links) and provides full-text search, content extraction, and relationship tracking.

## Development Commands

### Running the Server

```bash
# HTTP server (recommended for development and remote access)
python server_http.py
# Server runs at http://0.0.0.0:8000/mcp

# STDIO server (for local MCP clients like Claude CLI)
python server.py
```

### Testing

```bash
# Run basic end-to-end test
python test_basic.py

# Test creates content, adds metadata, searches, and extracts snippets
```

### Dependencies

```bash
# Install in editable mode
pip install -e .

# Install MCP and web server dependencies
pip install "mcp[cli]" starlette uvicorn
```

### Environment Variables

```bash
# Storage location (default: ~/.mcp_snippets)
export MCP_SNIPPETS_ROOT=/path/to/storage

# HTTP server configuration
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=8000
export MCP_HTTP_PATH=/mcp
```

## Architecture

### Core Design Principles

1. **File-based Storage**: All data stored in filesystem under `MCP_SNIPPETS_ROOT` - no database required
2. **Graph Model**: Content nodes connected via typed relationships (snippet_of, related_to)
3. **Immutable Nodes**: Content nodes written once, relationships added via append-only edge files
4. **TF-IDF Search**: Full-text search with inverted index, metadata filtering, and multiple sort modes

### Module Responsibilities

#### `storage.py` - Storage Layer
- **Purpose**: File-based persistence for all nodes and edges
- **Key Functions**:
  - `add_content()`: Create content node with UUID, write to `nodes/content/{uuid}.json`
  - `add_tag()`, `add_author()`, `add_link()`: Create metadata nodes with slugified IDs
  - `link_*()`: Append edges to JSONL files in `edges/`
  - `get_node()`: Retrieve node by ID from any type directory
  - `get_content_links()`: Resolve content→link edges and return link nodes
- **Storage Structure**:
  ```
  $MCP_SNIPPETS_ROOT/
  ├── nodes/
  │   ├── content/    # UUIDs (e.g., a1b2c3d4-e5f6-7890-abcd-ef1234567890.json)
  │   ├── tag/        # Slugs (e.g., machine-learning.json)
  │   ├── author/     # Slugs (e.g., jane-doe.json)
  │   ├── style/      # Slugs (e.g., blog.json)
  │   └── link/       # URL-based slugs
  ├── edges/          # Append-only JSONL files
  │   ├── relates.jsonl   # Content→Content (snippet_of, related_to)
  │   ├── tags.jsonl      # Content→Tag (is_tagged)
  │   ├── authors.jsonl   # Content→Author (authored)
  │   └── links.jsonl     # Content→Link (has_link)
  └── index/          # Search index files
      ├── inverted.json   # Token→{doc_id→term_freq}
      ├── doclens.json    # {doc_id→token_count}
      └── meta.json       # {doc_id→{date, title, style, tags, authors}}
  ```

#### `schemas.py` - Data Models
- **Purpose**: Define node types and normalization functions
- **Node Types**:
  - `ContentNode`: Full text + metadata (title, date, style, tags, authors, content)
  - `TagNode`: Tag name + slug
  - `StyleNode`: Style name (restricted to: chapter, blog, post, snippet, tweet)
  - `AuthorNode`: Name + social media handles (linkedin, twitter, substack, reddit)
  - `LinkNode`: URL + title + description
- **Key Functions**:
  - `slugify()`: Normalize text to lowercase-dash-separated format (e.g., "Machine Learning" → "machine-learning")
  - `ensure_style()`: Validate style is in allowed set: {chapter, blog, post, snippet, tweet}

#### `search.py` - Full-Text Search
- **Purpose**: TF-IDF based search with metadata filtering
- **Implementation**:
  - **Tokenization**: Lowercase, alphanumeric only, stopword removal (the, and, a, to, of, in, it, is, that, on, for, as, with, this, be)
  - **Indexing**: `index_document()` updates inverted index, doc lengths, and metadata cache
  - **Scoring**: `score(q,d) = Σ (tf_d,t * idf_t) / sqrt(doc_len_d)` - TF-IDF with document length normalization
  - **Filters**: Applied before scoring - supports style, tag, author, title substring, content substring, relates (by content ID)
  - **Sorting**: relevance (TF-IDF), date (ISO8601 descending), random (seeded shuffle)
- **Key Functions**:
  - `index_document()`: Add/update single document in index
  - `rebuild_index()`: Scan all content nodes and rebuild entire index
  - `search()`: Query with filters, return paginated results

#### `content_tools.py` - Content Extraction
- **Purpose**: Transform long-form content into snippets with various strategies
- **Extraction Tools**:
  - `extract_raw_content()`: Truncate with optional max_length
  - `extract_by_paragraph()`: Split on `\n\n`, filter by min_words
  - `extract_similar_sections()`: Find keyword matches, include context sentences
  - `extract_for_social_media()`: Heuristic selection of quotable sentences (questions, action words) with platform-specific character limits
  - `combine_related_snippets()`: Merge multiple snippets into long-form, union tags/authors
- **All extraction tools**:
  - Preserve tags/authors from source
  - Create `snippet_of` relationship to source
  - Return list of new content UUIDs

#### `server.py` - STDIO MCP Server
- **Purpose**: MCP server using STDIO transport (for local CLI clients)
- **Framework**: FastMCP with `transport="stdio"`
- **Tool Registration**: Each MCP tool wraps a storage/search/extraction function
- **Async Wrappers**: All tools are `async def` to satisfy MCP protocol

#### `server_http.py` - HTTP MCP Server
- **Purpose**: MCP server using HTTP transport (for remote clients, Codespaces)
- **Framework**: FastMCP with `host`, `port`, `streamable_http_path`
- **Configuration**: Reads `MCP_HTTP_HOST`, `MCP_HTTP_PORT`, `MCP_HTTP_PATH` env vars
- **Deployment**: Recommended for GitHub Codespaces, VS Code workspace, remote access

### Key Data Flows

#### Creating Content with Metadata
```
User → tool_add_content()
  ↓
storage.add_content()
  ↓
1. Generate UUID
2. Create ContentNode with metadata
3. Write nodes/content/{uuid}.json
4. For each tag: link_tag() → append to edges/tags.jsonl
5. For each author: link_author() → append to edges/authors.jsonl
6. index_document() → update inverted.json, doclens.json, meta.json
  ↓
Return UUID
```

#### Searching Content
```
User → tool_search(query, filters, sort)
  ↓
search.search()
  ↓
1. Load inverted.json, doclens.json, meta.json
2. Tokenize query
3. Apply filters (style, tag, author, title, content, relates) → candidate set
4. Score candidates with TF-IDF (if query provided)
5. Sort by: relevance/date/random
6. Paginate
7. Load full content nodes for page
  ↓
Return {items, total, page, page_size}
```

#### Extracting Social Media Snippets
```
User → tool_extract_for_social_media(content_id, platform, max_count)
  ↓
content_tools.extract_for_social_media()
  ↓
1. get_node(content_id) → load source content
2. Split content into sentences
3. Score sentences by heuristics:
   - Contains question mark?
   - Contains action words? (discover, learn, build, create, think, consider, imagine, remember)
   - Length in range [20, platform_max_length]?
4. For each good candidate (up to max_count):
   a. add_content() with sentence, inherit tags/authors, add [platform, "social-media"]
   b. link_relates(snippet_id, "snippet_of", content_id)
   c. Copy source links to snippet
  ↓
Return list of snippet UUIDs
```

## Common Development Tasks

### Adding a New MCP Tool

1. Implement core logic in `storage.py`, `search.py`, or `content_tools.py`
2. Add async wrapper in `server.py`:
   ```python
   @mcp.tool(
       title="Tool Name",
       description="""Detailed description with:
       - Parameters section
       - Returns section
       - Example usage
       - Notes/caveats
       """
   )
   async def tool_name(param: str, optional: Optional[int] = None) -> str:
       return core_function(param, optional)
   ```
3. Test with `python test_basic.py` or manual testing
4. Update CLAUDE.md (this file) if it changes architecture

### Modifying Search Behavior

- **Tokenization**: Edit `_tokenize()` in `search.py` - currently uses alphanumeric + stopword removal
- **Scoring**: Edit `_score()` in `search.py` - currently TF-IDF with doc length normalization
- **Filters**: Add new filter types in `search()` function - pattern: apply set intersection to `docset`
- **After changes**: Run `rebuild_index()` to update all documents

### Adding a New Node Type

1. Define dataclass in `schemas.py`:
   ```python
   @dataclass
   class NewNode:
       id: str
       type: str = "new_type"
       # ... fields
   ```
2. Add storage directory in `storage.py`:
   ```python
   NODE_DIRS = {
       # ...
       "new_type": ROOT / "nodes" / "new_type",
   }
   ```
3. Add creation function in `storage.py`:
   ```python
   def add_new_type(name: str, ...) -> str:
       slug = slugify(name)
       path = NODE_DIRS["new_type"] / f"{slug}.json"
       if not path.exists():
           _write_json(path, asdict(NewNode(id=slug, ...)))
       return slug
   ```
4. Add edge files if needed (e.g., `edges/new_type_edges.jsonl`)
5. Add MCP tool in `server.py`

### Debugging Search Issues

1. Check index exists: `ls -la $MCP_SNIPPETS_ROOT/index/`
2. Rebuild index: `python -c "from search import rebuild_index; rebuild_index()"`
3. Inspect index contents:
   ```python
   import json
   from pathlib import Path
   inv = json.loads(Path("~/.mcp_snippets/index/inverted.json").expanduser().read_text())
   meta = json.loads(Path("~/.mcp_snippets/index/meta.json").expanduser().read_text())
   print(f"Tokens indexed: {len(inv)}")
   print(f"Documents indexed: {len(meta)}")
   ```
4. Test tokenization:
   ```python
   from search import _tokenize
   print(_tokenize("Machine Learning and AI"))
   # Expected: ['machine', 'learning', 'ai'] (no stopwords)
   ```

## Important Conventions

### Tag Normalization
- **Always** use `slugify()` for tag names - ensures consistency
- Tags are case-insensitive: "Machine Learning" == "machine-learning"
- Spaces/punctuation become dashes: "AI & ML" → "ai-ml"

### Style Validation
- Styles **must** be in: {chapter, blog, post, snippet, tweet}
- `ensure_style()` raises ValueError for invalid styles
- Content can have multiple styles: `["blog", "post"]`

### Content IDs
- Content uses UUIDs: `str(uuid.uuid4())`
- Metadata nodes use slugs: `slugify(name)`
- UUIDs for content allow arbitrary metadata without conflicts

### Relationships
- `snippet_of`: Directional (snippet → parent)
- `related_to`: Bidirectional (content ↔ content)
- Always create relationship **after** both nodes exist

### Edge Files
- **Append-only**: Never modify existing lines, only append
- **JSONL format**: One JSON object per line
- All edges include: src/content, type, dst/tag/author/link, date (ISO8601)

## Testing

The `test_basic.py` file demonstrates complete workflows:

```bash
python test_basic.py
```

Tests cover:
1. Tag normalization (`slugify`)
2. Author creation with social handles
3. Content creation with metadata
4. URL linking to content
5. Content retrieval with links
6. Full-text search with filters
7. Paragraph extraction
8. Social media snippet extraction
9. Snippet metadata verification

**When adding features**: Extend `test_basic.py` with new test cases.

## MCP Server Deployment

### Local Development (STDIO)
```bash
python server.py
# Configure MCP client with: command="python", args=["server.py"]
```

### Local/Remote Development (HTTP)
```bash
python server_http.py
# Configure MCP client with: type="http", url="http://localhost:8000/mcp"
```

### GitHub Codespaces
```bash
python server_http.py
# Port 8000 auto-forwarded
# Make port public in Ports panel
# Configure MCP client with public URL
```

## Storage Considerations

### Scalability
- File-based storage works well for 10K-100K content nodes
- Beyond 100K nodes, consider:
  - Edge file pagination (split by date ranges)
  - Search index sharding (by tag or author)
  - SQLite migration for nodes (keep edge files for auditability)

### Backup/Export
- All data in `$MCP_SNIPPETS_ROOT`
- Simple backup: `tar -czf backup.tar.gz ~/.mcp_snippets/`
- Migration: Copy directory to new location, update `MCP_SNIPPETS_ROOT`

### Concurrency
- Single-writer pattern: One server process per storage directory
- Read-while-write safe: Atomic file replacement (`tmp.replace(path)`)
- Multi-reader safe: JSON files read atomically

## Troubleshooting

### "Node not found" errors
- Check content exists: `ls ~/.mcp_snippets/nodes/content/{uuid}.json`
- Verify UUID format (36 chars with hyphens)
- Check correct storage root: `echo $MCP_SNIPPETS_ROOT`

### Search returns no results
- Rebuild index: `python -c "from search import rebuild_index; rebuild_index()"`
- Check stopwords: Common words filtered out (the, and, a, to, of, in, it, is, that, on, for, as, with, this, be)
- Verify metadata filters: Tags/authors must match exactly (slugified)

### Import errors
- Install dependencies: `pip install -e .`
- Check virtual environment active: `which python`
- Verify Python version: `python --version` (3.9+)

### HTTP server won't start
- Check port not in use: `lsof -i :8000`
- Verify environment: `echo $MCP_HTTP_PORT`
- Try different port: `MCP_HTTP_PORT=8001 python server_http.py`
