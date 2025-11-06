# Quick Start: Connect to Claude

Your MCP Content Library server is running! Here's how to connect it to Claude.

## 🚀 Server Status

**Server Running:** ✅ Yes (port 8000)
**Local URL:** `http://localhost:8000/mcp`
**Public URL:** `https://ominous-rotary-phone-p7jgg5vq9rh465-8000.app.github.dev/mcp`

> Get fresh URL anytime: `./get-public-url.sh`

---

## Option 1: Claude CLI (Fastest Setup)

### Automated Setup
```bash
./setup-claude-cli.sh
```
This interactive script will:
- Create local config (`.claude/mcp_config.json`)
- Optionally set up global config
- Handle backups if config exists
- Guide you through the process

### Manual Setup (Local Config - This Project Only)
```bash
# Already done for you!
ls -la .claude/mcp_config.json  # ✅ File exists

# Use it:
export CLAUDE_MCP_CONFIG=.claude/mcp_config.json
claude chat
```

### Manual Setup (Global Config - All Projects)

**macOS/Linux:**
```bash
mkdir -p ~/.config/claude
cat > ~/.config/claude/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "content-library": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
EOF
```

**Then just:**
```bash
claude chat  # MCP server auto-loads!
```

### Verify It's Working
```bash
# List servers
claude mcp list-servers

# List tools
claude mcp list-tools content-library

# Test it
claude mcp call content-library tool_add_content \
  --content "My first snippet!" \
  --style '["snippet"]' \
  --tags '["test"]'
```

---

## Option 2: Claude Desktop

Claude Desktop is the native app (same interface as claude.ai, but supports MCP).

### Step 1: Find Your Config File

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
# Edit: claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 2: Add Configuration

**If server is LOCAL on your machine:**
```json
{
  "mcpServers": {
    "content-library": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**If server is in CODESPACES:**
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

> ⚠️ For Codespaces URL: Set port 8000 to "Public" in Ports panel!

### Step 3: Restart Claude Desktop

1. **Completely quit** Claude Desktop (not just close window)
2. **Reopen** Claude Desktop
3. Look for **🔌 icon** in the UI
4. Tools are now available!

### Step 4: Test It

Ask Claude:
> "Can you add a snippet to my content library with the content 'Testing MCP integration' and tag it 'test'?"

Claude should use the `tool_add_content` tool automatically!

---

## Option 3: Claude.ai Website

❌ **Not supported yet**

The claude.ai website doesn't support custom MCP servers. Use:
- **Claude Desktop** instead (same interface, native app)
- **Claude CLI** for terminal access

---

## 🧪 Testing Your Connection

### 1. Check Server is Running
```bash
curl http://localhost:8000/mcp
# Should return JSON with session info
```

### 2. Claude CLI Tests
```bash
# List your servers
claude mcp list-servers

# Expected output:
# - content-library (http://localhost:8000/mcp)

# List available tools
claude mcp list-tools content-library

# Expected: 15+ tools including tool_add_content, tool_search, etc.
```

### 3. Claude Desktop Test

1. Open Claude Desktop
2. Look for 🔌 icon
3. Ask: "What MCP tools do you have access to?"
4. Claude should list the content library tools

---

## 📚 Usage Examples

Once connected, try these prompts with Claude:

### Add Content
> "Add a blog post snippet to my content library with the title 'Product Strategy 101', tag it 'product-management', and author 'jane-doe'"

### Search
> "Search my content library for snippets tagged 'product-management'"

### Extract Social Content
> "Extract Twitter-optimized snippets from content ID [paste-id-here]"

### Combine Content
> "Combine these snippet IDs into a blog post: [id1], [id2], [id3] with the title 'Complete Guide'"

---

## 🔧 Troubleshooting

### Claude CLI: "Server not found"
```bash
# Check config exists
cat ~/.config/claude/mcp_config.json
# or
cat .claude/mcp_config.json

# Verify server running
lsof -i :8000

# Use local config explicitly
claude chat --mcp-config .claude/mcp_config.json
```

### Claude Desktop: No 🔌 icon
1. Check JSON syntax (use [jsonlint.com](https://jsonlint.com))
2. Verify file location is correct
3. Completely restart Claude Desktop (quit, not just close)
4. Check Claude Desktop logs for errors

### Public URL Not Working (Codespaces)
1. Check server is running: `lsof -i :8000`
2. Open **Ports** panel (View → Ports)
3. Right-click port 8000
4. Set **Port Visibility** → **Public**
5. Test: `curl https://your-url/mcp`

---

## 🎯 What's Next?

1. **Start Using It:**
   - Add your existing content to the library
   - Tag and organize your snippets
   - Extract social media content

2. **Explore Tools:**
   - See all 15+ tools in `README.md`
   - Full documentation in `CLAUDE.md`

3. **Customize:**
   - Adjust tags for your workflow
   - Create custom extraction workflows
   - Build your content graph

---

## 📁 Files Created

- `.claude/mcp_config.json` - Local Claude CLI config ✅
- `setup-claude-cli.sh` - Automated setup script
- `get-public-url.sh` - Get current public URL
- `MCP-URLS.md` - All URLs and endpoints

---

**Need Help?** See `README.md` → "Connecting to Claude" section for detailed instructions!
