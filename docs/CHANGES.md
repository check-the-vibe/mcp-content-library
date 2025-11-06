# Changes and Enhancements - v0.2.0

## Summary

This release significantly enhances the MCP Content Library with improved metadata handling, advanced content extraction tools, comprehensive documentation, and multi-provider support.

## New Features

### 1. Link Node Type
- **Added `LinkNode` schema** (schemas.py:47-53)
  - Stores URLs with optional title and description
  - Links associate with content nodes via `has_link` edges
- **New storage functions**:
  - `add_link()` - Create or retrieve link nodes
  - `link_url()` - Associate URLs with content
  - `get_content_links()` - Retrieve all links for content
- **New MCP tools**:
  - `tool_add_link` - Create link nodes
  - `tool_link_url` - Link URLs to content
- **Auto-included in responses**: `get_node` now returns links for content nodes

### 2. Strict Tag Normalization
- **Enhanced `slugify()` function** (schemas.py:56-73)
  - Enforces lowercase-only tags
  - Replaces spaces/punctuation with dashes
  - Collapses multiple dashes
  - Example: "Machine Learning!" → "machine-learning"
- **Comprehensive documentation** in function docstring

### 3. Advanced Content Extraction Tools

New module `content_tools.py` with 5 specialized extractors:

#### `extract_raw_content()`
- Extract with optional truncation
- Preserve or override metadata
- Configurable styles

#### `extract_by_paragraph()`
- Break content into paragraph-level snippets
- Minimum word count filtering
- Automatic `snippet_of` relationships

#### `extract_similar_sections()`
- Keyword-based section extraction
- Configurable context window (sentences before/after)
- Automatic topic tagging

#### `extract_for_social_media()`
- Platform-specific optimization (Twitter, LinkedIn, Instagram)
- Character limit enforcement
- Smart heuristics (questions, action words)
- Automatic URL copying

#### `combine_related_snippets()`
- Merge multiple snippets into long-form
- Union of metadata (tags, authors)
- Configurable separators
- Bidirectional relationships

### 4. Enhanced Tool Descriptions

All MCP tools now have comprehensive descriptions including:
- Detailed parameter documentation
- Return value specifications
- Example usage
- Use case scenarios
- Important notes and warnings

Affected tools:
- `tool_add_content` - 13-line detailed description
- `tool_add_tag`, `tool_add_style`, `tool_add_author` - Enhanced docs
- `tool_search` - Complete filter syntax reference
- `tool_get_node`, `tool_reindex` - Expanded documentation
- All relationship tools - Usage examples included

### 5. Multi-Provider Configuration

#### VS Code Integration
- **`.vscode/mcp.json`** created with two server configs:
  - `contentLibraryStdio` - Local STDIO server
  - `contentLibraryHttp` - HTTP server (localhost:8000)
- Workspace-relative paths using `${workspaceFolder}`
- Environment variable support

#### GitHub Codespaces
- **`.devcontainer/devcontainer.json`** created:
  - Python 3.11 environment
  - Automatic dependency installation
  - Port 8000 auto-forwarding
  - Pre-configured environment variables
  - VS Code extensions (Python, Pylance)

#### Claude CLI / Claude Desktop / Cline
- Configuration examples documented in CLAUDE.md
- Support for all transport types (STDIO, HTTP)
- Environment variable templates

### 6. Comprehensive Documentation

#### **CLAUDE.md** (new, 800+ lines)
Complete setup guide covering:
- Feature overview with examples
- Quick start instructions
- GitHub Codespaces setup (automatic)
- Local development setup
- Configuration for 5+ providers:
  - VS Code with GitHub Copilot
  - Claude CLI
  - Claude Desktop
  - Cline (VS Code Extension)
  - OpenCode (mentioned)
- All 15+ tools with full API documentation
- 4 usage examples (workflows)
- Architecture deep-dive
- Troubleshooting guide

#### **README.md** (updated)
- Simplified quick start
- Feature highlights
- Points to CLAUDE.md for complete docs
- Project structure overview

#### **requirements.txt** (new)
- Pinned dependencies
- Optional dev dependencies

#### **setup.py** (new)
- Package metadata
- Entry points for CLI
- Dependency declarations

### 7. Project Infrastructure

#### **start.sh** (new)
Convenience script for quick startup:
```bash
./start.sh       # Start HTTP server
./start.sh stdio # Start STDIO server
```
- Auto-creates venv
- Auto-installs dependencies
- Creates storage directory

#### **test_basic.py** (new)
End-to-end test suite:
- Tag normalization
- Content creation with metadata
- URL linking
- Search functionality
- Content extraction (paragraphs, social)
- Relationship verification
- All tests passing ✓

## Technical Improvements

### Storage Layer
- Added `link` node directory to `NODE_DIRS`
- New edge file: `edges/links.jsonl`
- Updated `get_node()` to search link nodes
- Enhanced content retrieval with link embedding

### Server Configuration
- Environment variable support expanded:
  - `MCP_HTTP_HOST` - Bind address
  - `MCP_HTTP_PORT` - Port number
  - `MCP_HTTP_PATH` - Endpoint path
  - `MCP_SNIPPETS_ROOT` - Storage location
- Dynamic path resolution with `_ensure_path()`

### Code Quality
- Comprehensive type hints throughout
- Detailed docstrings for all new functions
- Dataclass usage for structured schemas
- Error handling for missing nodes

## Files Added
1. `content_tools.py` - Content extraction utilities
2. `CLAUDE.md` - Complete documentation
3. `CHANGES.md` - This file
4. `.vscode/mcp.json` - VS Code configuration
5. `.devcontainer/devcontainer.json` - Codespaces config
6. `setup.py` - Package setup
7. `requirements.txt` - Dependencies
8. `start.sh` - Startup script
9. `test_basic.py` - Test suite

## Files Modified
1. `schemas.py` - Added LinkNode, enhanced slugify
2. `storage.py` - Link node support, new functions
3. `server.py` - New tools, enhanced descriptions
4. `README.md` - Rewritten for v0.2.0

## Breaking Changes

None - All changes are backward compatible. Existing content nodes, tags, authors, and relationships continue to work without modification.

## Migration Notes

No migration required. New features are opt-in:
- Existing installations can upgrade by pulling latest code
- No database schema changes (file-based storage)
- New link nodes are optional
- Old content nodes work with new extraction tools

## Testing

All functionality verified with `test_basic.py`:
- 9 test scenarios
- All tests passing
- Covers: normalization, CRUD, search, extraction, relationships

## Performance

No performance regressions:
- File-based storage remains lightweight
- Search indexing unchanged (TF-IDF)
- New tools operate on-demand (not background)
- Link retrieval adds minimal overhead

## Future Enhancements

Documented in CLAUDE.md:
- Richer edge queries (directional, distance)
- Tone adaptation tools (mentioned in original spec)
- MCP resource endpoints
- Export/import bundles
- Comprehensive test suite expansion

## Credits

Based on original specification in `.init/INSTRUCTIONS.md`

Enhancements implemented:
- Tag normalization with strict rules
- Link node type with URL tracking
- Advanced content extraction (5 tools)
- Multi-provider configuration
- Comprehensive documentation

---

**Version**: 0.2.0
**Date**: 2025-11-05
**Python**: 3.9+
**MCP SDK**: 1.20.0+
