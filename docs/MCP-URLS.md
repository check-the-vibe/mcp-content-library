# MCP Server URLs - Quick Reference

## Current Server Status

✅ **Server is running** on port 8000

## Available Endpoints

### 1. Localhost (for VS Code / within Codespace)
```
http://localhost:8000/mcp
```
**Use this for:**
- VS Code MCP configuration (already configured in `.vscode/mcp.json`)
- Local testing within the Codespace
- Any client running in the same container

### 2. Public URL (for external access)
```
https://ominous-rotary-phone-p7jgg5vq9rh465-8000.app.github.dev/mcp
```
**Use this for:**
- Claude Desktop (running on your local machine)
- Claude CLI (if installed locally, not in Codespace)
- Cline or other external MCP clients
- Remote access from outside Codespaces

⚠️ **Important:** For the public URL to work, you must:
1. Open the **Ports** panel in VS Code (View → Ports)
2. Find port 8000
3. Right-click → **Port Visibility** → **Public**

## Configuration Examples

### VS Code (Current Configuration)
Located in `.vscode/mcp.json`:
```json
{
  "servers": {
    "contentLibraryHttp": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```
✅ Already working!

### Claude Desktop (Local Machine)
Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "content-library": {
      "type": "http",
      "url": "https://ominous-rotary-phone-p7jgg5vq9rh465-8000.app.github.dev/mcp"
    }
  }
}
```

### Claude CLI
Add to `~/.config/claude/mcp_config.json`:
```json
{
  "mcpServers": {
    "content-library": {
      "type": "http",
      "url": "https://ominous-rotary-phone-p7jgg5vq9rh465-8000.app.github.dev/mcp"
    }
  }
}
```

## Server Management

### Check if server is running:
```bash
lsof -i :8000
# or
cat server.log
```

### Start the server:
```bash
./start.sh           # Recommended
# or
python server_http.py
```

### Stop the server:
```bash
kill $(cat server.pid)
# or
pkill -f server_http.py
```

### View server logs:
```bash
tail -f server.log
```

### Get fresh public URL:
```bash
./get-public-url.sh
```

## Testing the Connection

### From within Codespace:
```bash
curl http://localhost:8000/mcp
```

### From external (after setting port to Public):
```bash
curl https://ominous-rotary-phone-p7jgg5vq9rh465-8000.app.github.dev/mcp
```

Both should return a session ID response.

## Available Tools

The server exposes **15+ MCP tools** including:

**Content Management:**
- `tool_add_content` - Create content with metadata
- `tool_add_link` - Create link nodes
- `tool_link_url` - Associate URLs with content
- `tool_search` - Full-text search with filters
- `tool_get_node` - Retrieve any node by ID

**Content Extraction:**
- `tool_extract_raw_content` - Extract with truncation
- `tool_extract_by_paragraph` - Break into paragraphs
- `tool_extract_similar_sections` - Keyword-based extraction
- `tool_extract_for_social_media` - Platform-optimized snippets
- `tool_combine_related_snippets` - Merge snippets

**Relationships:**
- `tool_link_relates` - Create content relationships
- `tool_link_tag` - Tag content
- `tool_link_author` - Associate authors

**Utilities:**
- `tool_add_tag`, `tool_add_style`, `tool_add_author`
- `tool_reindex` - Rebuild search index

See **CLAUDE.md** for complete documentation.

---

**Last Updated:** 2025-11-05
**Server Status:** ✅ Running
**Port:** 8000
