# MCP Content Library

A Model Context Protocol (MCP) server for managing writing content, snippets, and building instant context for AI-assisted writing.

## 🚀 Quick Start (One Command)

```bash
git clone https://github.com/check-the-vibe/mcp-content-library.git
cd mcp-content-library
./bootstrap.sh
```

The bootstrap script will:
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Install Claude CLI (if available)
- ✅ Configure MCP connection
- ✅ Provide setup instructions for Codex & OpenCode

**That's it!** The server will be ready to run.

### Alternative Installation Methods

<details>
<summary><b>🐳 Docker Compose (Recommended for Production)</b></summary>

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

Server runs at `http://localhost:8000/`

</details>

<details>
<summary><b>⚙️ Systemd Service (Linux Auto-Start)</b></summary>

```bash
# Run bootstrap first
./bootstrap.sh

# Install systemd service
./install-systemd.sh

# Service commands
sudo systemctl status mcp-content-library@$USER
sudo systemctl restart mcp-content-library@$USER
sudo journalctl -u mcp-content-library@$USER -f
```

The service will auto-start on boot and restart on failure.

</details>

<details>
<summary><b>📝 Manual Installation</b></summary>

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install -r requirements.txt

# Create storage directory
mkdir -p ~/.mcp_snippets

# Run server
python server_http.py
```

</details>

## 🌐 Accessing the Server

Once running, the server provides multiple endpoints:

| Endpoint | Purpose | URL |
|----------|---------|-----|
| **Web UI** | Friendly dashboard with setup instructions | `http://localhost:8000/` |
| **MCP Protocol** | Connect AI clients here | `http://localhost:8000/mcp` |
| **Health Check** | Monitor server status | `http://localhost:8000/health` |

### Public Access (GitHub Codespaces / Cloud)

When running in Codespaces or cloud environments:

```bash
# Get your public URL
./get-public-url.sh
```

**Important:** Make sure port 8000 is set to "Public" visibility in your Codespaces Ports panel.

The web UI at `/` automatically detects and displays your public URL!

## 🤖 Connecting AI Clients

### Claude CLI (Recommended)

After running `./bootstrap.sh`, Claude CLI is automatically configured:

```bash
# Start the MCP server
./start.sh

# In another terminal, use Claude
export CLAUDE_MCP_CONFIG=.claude/mcp_config.json
claude chat
```

**Manual Claude CLI Installation:**
```bash
# Via npm (recommended)
npm install -g @anthropic-ai/claude-cli

# Or via pip
pip install claude-cli
```

### Claude Desktop & VS Code

Add to your MCP configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`  
**VS Code:** `.vscode/mcp.json`

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

For **remote/cloud servers**, replace `localhost:8000` with your public URL.

Restart Claude Desktop or reload VS Code after configuration.

### OpenAI Codex

```bash
# Install OpenAI Python library
pip install openai

# Set your API key
export OPENAI_API_KEY='your-api-key-here'

# Use in your Python code
import openai
# Configure to use your MCP endpoint
```

**Documentation:** https://platform.openai.com/docs/guides/code

### Qwen2.5-Coder (OpenCode)

```bash
# Install dependencies
pip install transformers torch

# Download and use model
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-Coder-7B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-7B-Instruct")
```

**Documentation:** https://github.com/QwenLM/Qwen2.5-Coder

## ✨ Features

- **Content Management**: Store and organize content from tweets to full chapters
- **Graph Relationships**: Link snippets to parent content with typed relationships
- **Rich Metadata**: Tags, authors, writing styles, and source URL tracking
- **Full-Text Search**: TF-IDF search with advanced filtering and sorting
- **Content Extraction**: Break down long-form into snippets with multiple strategies
- **Social Media Tools**: Extract platform-optimized snippets (Twitter, LinkedIn, Instagram)
- **Link Tracking**: Associate URLs with content for source attribution

## Connecting to Claude

### 🌟 New! Visit the Web UI

**Just open `http://localhost:8000/` in your browser!**

The landing page includes:
- ✅ Server status and health check
- 📊 Content statistics
- 🔗 All endpoint URLs (auto-detects public URL)
- 📖 Quick setup guides for Claude, Codex, and OpenCode
- 💻 Copy-paste configuration snippets

This is especially useful when sharing your server publicly via Codespaces or cloud hosting.

---

### Detailed Claude Setup (Legacy Documentation)

### Option 1: Claude CLI (Recommended for this project)

The Claude CLI allows you to use MCP servers from the command line.

#### A. Local Configuration (Project-Specific)

Create a Claude config file in this project:

```bash
# Create config directory
mkdir -p .claude

# Create the MCP configuration
cat > .claude/mcp_config.json << 'EOF'
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

**Usage:**
```bash
# Start the server
./start.sh

# In another terminal, use Claude CLI with the local config
export CLAUDE_MCP_CONFIG=.claude/mcp_config.json
claude chat

# Or specify it per-command
claude chat --mcp-config .claude/mcp_config.json
```

#### B. Global Configuration (All Projects)

Add to your global Claude config at `~/.config/claude/mcp_config.json`:

**For local development:**
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

**For GitHub Codespaces (public URL):**
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

> **Note:** To get your current public URL, run `./get-public-url.sh`

**Usage:**
```bash
# Just use Claude CLI normally - MCP server is auto-loaded
claude chat
```

### Option 2: Claude Desktop

Claude Desktop is the native app for macOS and Windows.

#### Configuration

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

**For local server:**
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

**For GitHub Codespaces (if server is running there):**
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

> ⚠️ **Important:** For Codespaces URL to work, you must:
> 1. Ensure server is running: `./start.sh`
> 2. Open **Ports** panel in VS Code (View → Ports)
> 3. Right-click port 8000 → **Port Visibility** → **Public**

#### Activate the Server

1. Save the configuration file
2. **Restart Claude Desktop completely** (quit and reopen)
3. Look for the 🔌 plug icon in the UI - this indicates MCP servers are loaded
4. The content library tools will appear automatically in your conversations

### Option 3: Claude.ai Website

> ⚠️ **Note:** The claude.ai website does **not** currently support custom MCP servers. MCP servers must run locally and connect via Claude Desktop or Claude CLI.

If you want to use this with claude.ai, you'll need to use one of these workarounds:
- Use **Claude Desktop** instead (same web interface, but native app)
- Use **Claude CLI** for terminal-based access
- Wait for Anthropic to add custom MCP support to claude.ai

### Verification

After configuring, verify the connection:

#### Claude CLI
```bash
# List available MCP servers
claude mcp list-servers

# List tools from the content library
claude mcp list-tools content-library

# Test adding content
claude mcp call content-library tool_add_content \
  --content "Test snippet" \
  --style '["snippet"]' \
  --tags '["test"]'
```

#### Claude Desktop
1. Open Claude Desktop
2. Start a new conversation
3. Look for the 🔌 icon (indicates MCP servers loaded)
4. Try asking: "Can you add a test snippet to my content library with the tag 'test'?"
5. Claude should use the `tool_add_content` tool automatically

### Getting Your Public URL

If you're running in GitHub Codespaces and need the public URL:

```bash
./get-public-url.sh
```

This will display your current public URL that you can use in any Claude client config.

### Troubleshooting

**Claude CLI not finding server:**
- Verify config file location: `cat ~/.config/claude/mcp_config.json`
- Check server is running: `curl http://localhost:8000/mcp`
- Try using local config: `claude chat --mcp-config .claude/mcp_config.json`

**Claude Desktop not showing tools:**
- Restart Claude Desktop completely
- Check JSON syntax in config file (use a JSON validator)
- Ensure URL is correct and server is accessible
- Look for error messages in Claude Desktop's logs

**Public URL not working:**
- Ensure server is running: `lsof -i :8000`
- Check port visibility is set to "Public" in Codespaces
- Test URL: `curl https://your-url/mcp`

## Documentation

**For complete setup instructions, configuration for all providers (VS Code, Claude CLI, Claude Desktop, Cline), API reference, and usage examples, see:**

### [📖 CLAUDE.md - Complete Setup Guide](./CLAUDE.md)

The guide covers:
- GitHub Codespaces setup (automatic)
- Local development setup
- Configuration for VS Code, Claude CLI, Claude Desktop, Cline
- All available tools and parameters
- Usage examples and workflows
- Architecture and troubleshooting

## GitHub Codespaces

This project is optimized for Codespaces with automatic:
- Dependency installation
- Port forwarding (port 8000)
- Environment configuration

Just create a Codespace and run `python server_http.py`!

## Project Structure

```
├── server.py           # STDIO server
├── server_http.py      # HTTP server
├── storage.py          # File-based storage
├── schemas.py          # Data models
├── search.py           # Full-text search
├── content_tools.py    # Content extraction
├── .vscode/mcp.json    # VS Code configuration
└── CLAUDE.md           # Complete documentation
```

## Available Tools (Preview)

- **Content**: `add_content`, `get_node`, `search`
- **Links**: `add_link`, `link_url`
- **Extraction**: `extract_by_paragraph`, `extract_for_social_media`, `extract_similar_sections`
- **Relationships**: `link_relates`, `link_tag`, `link_author`
- **Utilities**: `reindex`, `combine_related_snippets`

See [CLAUDE.md](./CLAUDE.md) for full documentation.

## License

MIT License - See LICENSE file for details
